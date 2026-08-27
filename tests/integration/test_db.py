import pytest
from sqlalchemy import text

from app.db.engine import check_db_connection, session_scope, transaction


def test_db_connection():
    assert check_db_connection() is True


def test_transaction_commit():
    with transaction() as session:
        result = session.execute(text("SELECT 1 as val"))
        assert result.fetchone().val == 1


def test_transaction_rollback_on_error():
    class IntentionalError(Exception):
        pass

    with pytest.raises(IntentionalError):
        with transaction() as session:
            session.execute(text("SELECT 1"))
            raise IntentionalError("rollback test")


def test_session_scope_explicit_commit(db_session):
    db_session.execute(text("SELECT 42 as answer"))
    db_session.commit()


def test_session_scope_explicit_rollback(db_session):
    db_session.execute(text("SELECT 1"))
    db_session.rollback()
