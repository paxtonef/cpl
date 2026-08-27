from sqlalchemy import text

from app.db.engine import session_scope, transaction


def test_transaction_isolation():
    with transaction() as session:
        result = session.execute(text("SELECT 1 as one"))
        assert result.fetchone().one == 1


def test_session_scope_caller_controls_commit():
    with session_scope() as session:
        result = session.execute(text("SELECT 2 as two"))
        assert result.fetchone().two == 2
        session.commit()
