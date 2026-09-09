"""B6 Concurrency Verification — REQ-B6-088 (RC-B6-02's closure).

Mirrors test_b3_concurrency.py's pattern: these tests need two
genuinely independent, auto-committing database connections, since
db_session wraps everything in an outer transaction that never
actually commits at the PostgreSQL level."""
import threading
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.cpl.runners.execution import admit_execution
from app.cpl.runners.outcomes import RunnerOutcome
from app.config import settings
from app.db.engine import check_db_connection

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


@pytest.fixture
def live_sessions():
    engine = create_engine(str(settings.database_url), pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    s1, s2 = Session(), Session()
    created = {"contacts": [], "assets": [], "cases": []}
    yield s1, s2, created
    for cid in created["cases"]:
        s1.execute(text("DELETE FROM cpl.runner_governance_decisions WHERE execution_id IN "
                         "(SELECT execution_id FROM cpl.runner_executions WHERE case_id = :c)"), {"c": str(cid)})
        s1.execute(text("DELETE FROM cpl.runner_executions WHERE case_id = :c"), {"c": str(cid)})
        s1.execute(text("DELETE FROM cpl.cases WHERE case_id = :c"), {"c": str(cid)})
    s1.commit()
    for aid in created["assets"]:
        s1.execute(text("DELETE FROM cpl.assets WHERE asset_id = :a"), {"a": str(aid)})
    for cid in created["contacts"]:
        s1.execute(text("DELETE FROM cpl.contacts WHERE contact_id = :c"), {"c": str(cid)})
    s1.commit()
    s1.close()
    s2.close()
    engine.dispose()


def _setup(session, created):
    from app.cpl.models.contact import Contact
    from app.cpl.models.asset import Asset
    from app.cpl.models.case import Case

    contact = Contact(contact_type="PERSON", display_name="Concurrency Test")
    session.add(contact)
    session.flush()
    asset = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
    session.add(asset)
    session.flush()
    case = Case(primary_contact_id=contact.contact_id, asset_id=asset.asset_id, domain="AUTOMOTIVE", case_type="DIAGNOSTIC")
    session.add(case)
    session.flush()
    session.commit()
    created["contacts"].append(contact.contact_id)
    created["assets"].append(asset.asset_id)
    created["cases"].append(case.case_id)
    return contact, asset, case


class TestB6Concurrency:

    def test_c01_concurrent_admission_same_key_resolves_to_one_row_no_raw_error(self, live_sessions, full_b6_authority):
        """REQ-B6-088: two independent connections race to admit an
        execution with the same (runner_type, idempotency_key). Exactly
        one canonical row must result, and NEITHER caller may observe a
        raw database error — this is the exact scenario RC-B6-02 found
        unaddressed in v0 and R-B6-R02 was written to close."""
        s1, s2, created = live_sessions
        contact, asset, case = _setup(s1, created)
        key = str(uuid.uuid4())

        results = {}
        barrier = threading.Barrier(2)

        def _attempt(session, label):
            barrier.wait()
            try:
                r = admit_execution(
                    session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                    runner_version="1.0", execution_purpose="race", idempotency_key=key, authority=full_b6_authority,
                )
                session.commit()
                results[label] = ("ok", r)
            except Exception as exc:  # noqa: BLE001 — this is exactly what must never happen
                session.rollback()
                results[label] = ("raw_error", exc)

        t1 = threading.Thread(target=_attempt, args=(s1, "t1"))
        t2 = threading.Thread(target=_attempt, args=(s2, "t2"))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Neither thread may have surfaced a raw error.
        assert results["t1"][0] == "ok", f"t1 raised: {results['t1'][1]}"
        assert results["t2"][0] == "ok", f"t2 raised: {results['t2'][1]}"

        r1, r2 = results["t1"][1], results["t2"][1]
        assert r1.outcome == RunnerOutcome.SUCCESS
        assert r2.outcome == RunnerOutcome.SUCCESS
        assert r1.object_id == r2.object_id  # exactly one canonical execution

        from app.cpl.models.runner_execution import RunnerExecution
        s1.expire_all()
        count = s1.query(RunnerExecution).filter(
            RunnerExecution.runner_type == "VIR", RunnerExecution.idempotency_key == key,
        ).count()
        assert count == 1  # no duplicate row survived the race
