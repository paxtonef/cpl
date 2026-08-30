"""B2 Positive Verification — P01 through P20."""
import pytest
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from app.db.base import Base
from app.db.engine import check_db_connection
from app.cpl.models.contact import Contact
from app.cpl.models.contact_point import ContactPoint
from app.cpl.models.account import Account
from app.cpl.models.asset import Asset
from app.cpl.models.asset_identifier import AssetIdentifier
from app.cpl.models.contact_asset_relationship import ContactAssetRelationship
from app.cpl.models.case import Case
from app.cpl.models.case_participant import CaseParticipant
from app.cpl.models.runner_execution import RunnerExecution
from app.cpl.models.runner_artifact import RunnerArtifact
from app.cpl.models.case_event import CaseEvent
from app.cpl.models.asset_identity_resolution import AssetIdentityResolution
from app.automotive.models.vehicle_detail import VehicleDetail

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


class TestB2Positive:
    """Mandatory positive verification set P01–P20."""

    def test_p01_create_person_contact(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Alice", first_name="Alice", last_name="Smith")
        db_session.add(c)
        db_session.commit()
        assert c.contact_id is not None
        assert c.contact_status == "ACTIVE"

    def test_p02_create_organization_contact(self, db_session):
        c = Contact(contact_type="ORGANIZATION", display_name="Acme Corp")
        db_session.add(c)
        db_session.commit()
        assert c.contact_id is not None
        assert c.contact_type == "ORGANIZATION"

    def test_p03_create_multiple_accounts_for_one_contact(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Bob")
        db_session.add(c)
        db_session.commit()
        a1 = Account(contact_id=c.contact_id, auth_provider="google", provider_subject_id="bob1", account_status="ACTIVE")
        a2 = Account(contact_id=c.contact_id, auth_provider="apple", provider_subject_id="bob2", account_status="ACTIVE")
        db_session.add_all([a1, a2])
        db_session.commit()
        assert a1.account_id != a2.account_id

    def test_p04_create_multiple_contact_points_for_one_contact(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Carol")
        db_session.add(c)
        db_session.commit()
        cp1 = ContactPoint(contact_id=c.contact_id, point_type="EMAIL", raw_value="c@x.com", normalized_value="c@x.com", is_primary=True)
        cp2 = ContactPoint(contact_id=c.contact_id, point_type="PHONE", raw_value="+331", normalized_value="+331", is_primary=True)
        db_session.add_all([cp1, cp2])
        db_session.commit()
        assert cp1.contact_point_id is not None
        assert cp2.contact_point_id is not None

    def test_p05_create_generic_non_automotive_asset(self, db_session):
        a = Asset(asset_domain="THERMAL_SYSTEM", asset_type="THERMOSIPHON", asset_status="ACTIVE", display_name="Heater X")
        db_session.add(a)
        db_session.commit()
        assert a.asset_id is not None
        assert a.asset_domain == "THERMAL_SYSTEM"

    def test_p06_create_automotive_asset(self, db_session):
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE", display_name="Peugeot 3008")
        db_session.add(a)
        db_session.commit()
        assert a.asset_id is not None
        assert a.asset_domain == "AUTOMOTIVE"

    def test_p07_attach_multiple_asset_identifiers(self, db_session):
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
        db_session.add(a)
        db_session.commit()
        ai1 = AssetIdentifier(asset_id=a.asset_id, identifier_type="VIN", identifier_value="VF3ABC", normalized_value="VF3ABC")
        ai2 = AssetIdentifier(asset_id=a.asset_id, identifier_type="REGISTRATION_NUMBER", identifier_value="AB-123-CD", normalized_value="AB123CD")
        db_session.add_all([ai1, ai2])
        db_session.commit()
        assert ai1.asset_identifier_id is not None
        assert ai2.asset_identifier_id is not None

    def test_p08_associate_contact_a_with_asset(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Owner A")
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
        db_session.add_all([c, a])
        db_session.commit()
        r = ContactAssetRelationship(contact_id=c.contact_id, asset_id=a.asset_id, relationship_type="OWNER", relationship_status="ACTIVE")
        db_session.add(r)
        db_session.commit()
        assert r.relationship_id is not None

    def test_p09_associate_contact_b_with_same_asset(self, db_session):
        c1 = Contact(contact_type="PERSON", display_name="Owner")
        c2 = Contact(contact_type="PERSON", display_name="Driver")
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
        db_session.add_all([c1, c2, a])
        db_session.commit()
        r1 = ContactAssetRelationship(contact_id=c1.contact_id, asset_id=a.asset_id, relationship_type="OWNER", relationship_status="ACTIVE")
        r2 = ContactAssetRelationship(contact_id=c2.contact_id, asset_id=a.asset_id, relationship_type="DRIVER", relationship_status="ACTIVE")
        db_session.add_all([r1, r2])
        db_session.commit()
        assert r1.relationship_id != r2.relationship_id

    def test_p10_associate_one_contact_with_multiple_assets(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Multi Owner")
        a1 = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
        a2 = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
        db_session.add_all([c, a1, a2])
        db_session.commit()
        r1 = ContactAssetRelationship(contact_id=c.contact_id, asset_id=a1.asset_id, relationship_type="OWNER", relationship_status="ACTIVE")
        r2 = ContactAssetRelationship(contact_id=c.contact_id, asset_id=a2.asset_id, relationship_type="OWNER", relationship_status="ACTIVE")
        db_session.add_all([r1, r2])
        db_session.commit()
        assert r1.asset_id != r2.asset_id

    def test_p11_create_vehicle_detail_projection(self, db_session):
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
        db_session.add(a)
        db_session.commit()
        vd = VehicleDetail(asset_id=a.asset_id, make="Peugeot", model="3008", vin_display="VF3ABC")
        db_session.add(vd)
        db_session.commit()
        assert vd.asset_id == a.asset_id

    def test_p12_create_case(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Requester")
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
        db_session.add_all([c, a])
        db_session.commit()
        case = Case(primary_contact_id=c.contact_id, asset_id=a.asset_id, domain="AUTOMOTIVE", case_type="DIAGNOSTIC", title="Engine noise")
        db_session.add(case)
        db_session.commit()
        assert case.case_id is not None
        assert case.case_status == "OPEN"

    def test_p13_add_case_participant(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Requester")
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
        db_session.add_all([c, a])
        db_session.commit()
        case = Case(primary_contact_id=c.contact_id, asset_id=a.asset_id, domain="AUTOMOTIVE", case_type="DIAGNOSTIC")
        db_session.add(case)
        db_session.commit()
        p = CaseParticipant(case_id=case.case_id, contact_id=c.contact_id, participant_role="REQUESTER")
        db_session.add(p)
        db_session.commit()
        assert p.case_participant_id is not None

    def test_p14_create_multiple_runner_executions_for_one_case(self, db_session):
        c = Contact(contact_type="PERSON", display_name="User")
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
        db_session.add_all([c, a])
        db_session.commit()
        case = Case(primary_contact_id=c.contact_id, asset_id=a.asset_id, domain="AUTOMOTIVE", case_type="DIAGNOSTIC")
        db_session.add(case)
        db_session.commit()
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        e1 = RunnerExecution(case_id=case.case_id, asset_id=a.asset_id, runner_type="VEHICLE_PGDR", runner_version="2.0.0", execution_status="COMPLETED", started_at=now, completed_at=now)
        e2 = RunnerExecution(case_id=case.case_id, asset_id=a.asset_id, runner_type="VEHICLE_PGDR", runner_version="2.1.0", execution_status="COMPLETED", started_at=now, completed_at=now)
        db_session.add_all([e1, e2])
        db_session.commit()
        assert e1.execution_id != e2.execution_id

    def test_p15_persist_runner_artifact_jsonb(self, db_session):
        c = Contact(contact_type="PERSON", display_name="User")
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
        db_session.add_all([c, a])
        db_session.commit()
        case = Case(primary_contact_id=c.contact_id, asset_id=a.asset_id, domain="AUTOMOTIVE", case_type="DIAGNOSTIC")
        db_session.add(case)
        db_session.commit()
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        e = RunnerExecution(case_id=case.case_id, asset_id=a.asset_id, runner_type="VEHICLE_PGDR", runner_version="2.0.0", execution_status="COMPLETED", started_at=now, completed_at=now)
        db_session.add(e)
        db_session.commit()
        art = RunnerArtifact(execution_id=e.execution_id, artifact_type="PGDR_CANONICAL_STATE", schema_name="pgdr_state", schema_version="3", payload={"status": "ok", "codes": ["P0301"]}, artifact_status="VALIDATED")
        db_session.add(art)
        db_session.commit()
        assert art.artifact_id is not None
        assert art.payload == {"status": "ok", "codes": ["P0301"]}

    def test_p16_append_multiple_case_events(self, db_session):
        c = Contact(contact_type="PERSON", display_name="User")
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
        db_session.add_all([c, a])
        db_session.commit()
        case = Case(primary_contact_id=c.contact_id, asset_id=a.asset_id, domain="AUTOMOTIVE", case_type="DIAGNOSTIC")
        db_session.add(case)
        db_session.commit()
        ev1 = CaseEvent(case_id=case.case_id, event_type="CASE_CREATED", actor_type="SYSTEM")
        ev2 = CaseEvent(case_id=case.case_id, event_type="CASE_STATUS_CHANGED", actor_type="SYSTEM", payload={"from": "OPEN", "to": "IN_PROGRESS"})
        db_session.add_all([ev1, ev2])
        db_session.commit()
        assert ev1.event_id is not None
        assert ev2.event_id is not None

    def test_p17_append_multiple_asset_identity_resolutions(self, db_session):
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
        db_session.add(a)
        db_session.commit()
        r1 = AssetIdentityResolution(asset_id=a.asset_id, resolver_type="VIR", resolver_version="1.0", resolution_status="RESOLVED", canonical_identity_payload={"vin": "VF3ABC"})
        r2 = AssetIdentityResolution(asset_id=a.asset_id, resolver_type="VIR", resolver_version="2.0", resolution_status="RESOLVED", canonical_identity_payload={"vin": "VF3ABC"})
        db_session.add_all([r1, r2])
        db_session.commit()
        assert r1.resolution_id is not None
        assert r2.resolution_id is not None

    def test_p18_set_current_asset_resolution_pointer(self, db_session):
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
        db_session.add(a)
        db_session.commit()
        r = AssetIdentityResolution(asset_id=a.asset_id, resolver_type="VIR", resolver_version="1.0", resolution_status="RESOLVED", canonical_identity_payload={"vin": "VF3ABC"})
        db_session.add(r)
        db_session.commit()
        a.current_identity_resolution_id = r.resolution_id
        db_session.commit()
        assert a.current_identity_resolution_id == r.resolution_id

    def test_p19_set_current_case_execution_pointer(self, db_session):
        c = Contact(contact_type="PERSON", display_name="User")
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
        db_session.add_all([c, a])
        db_session.commit()
        case = Case(primary_contact_id=c.contact_id, asset_id=a.asset_id, domain="AUTOMOTIVE", case_type="DIAGNOSTIC")
        db_session.add(case)
        db_session.commit()
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        e = RunnerExecution(case_id=case.case_id, asset_id=a.asset_id, runner_type="VEHICLE_PGDR", runner_version="2.0.0", execution_status="COMPLETED", started_at=now, completed_at=now)
        db_session.add(e)
        db_session.commit()
        case.current_execution_id = e.execution_id
        db_session.commit()
        assert case.current_execution_id == e.execution_id

    def test_p20_retrieve_persisted_data_from_new_session(self, db_engine):
        """Persistence across separate database sessions."""
        import uuid
        from datetime import datetime, timezone
        Session = sessionmaker(bind=db_engine)
        tag = f"P20-{uuid.uuid4().hex[:8]}"
        with Session() as s1:
            c = Contact(contact_type="PERSON", display_name=tag, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
            s1.add(c)
            s1.commit()
            contact_id = c.contact_id

        with Session() as s2:
            c = s2.query(Contact).filter_by(contact_id=contact_id).first()
            assert c is not None
            assert c.contact_type == "PERSON"
            assert c.display_name == tag
            s2.delete(c)
            s2.commit()
