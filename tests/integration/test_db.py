import pytest
from sqlalchemy import text

from app.db.engine import check_db_connection, transaction, session_scope


def test_check_db_connection():
    result = check_db_connection()
    assert isinstance(result, bool)


@pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")
def test_transaction_commit(db_engine):
    with transaction() as session:
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")
def test_transaction_rollback(db_engine):
    from sqlalchemy import Column, Integer
    from sqlalchemy.orm import declarative_base
    TempBase = declarative_base()
    class Dummy(TempBase):
        __tablename__ = "dummy_b1_test"
        id = Column(Integer, primary_key=True)
    Dummy.__table__.create(db_engine)
    try:
        with transaction() as session:
            session.execute(text("INSERT INTO dummy_b1_test (id) VALUES (1)"))
            raise RuntimeError("force rollback")
    except RuntimeError:
        pass
    with transaction() as session:
        result = session.execute(text("SELECT COUNT(*) FROM dummy_b1_test"))
        assert result.scalar() == 0
    Dummy.__table__.drop(db_engine)


@pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")
def test_session_scope_commit(db_engine):
    with session_scope() as session:
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1
        session.commit()


@pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")
def test_session_scope_rollback(db_engine):
    with session_scope() as session:
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1
