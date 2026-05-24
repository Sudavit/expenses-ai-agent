from collections.abc import Generator

from fastapi import Depends, Header, Query
from sqlmodel import Session, SQLModel, create_engine

from expenses_ai_agent.storage.repo import DBExpenseRepository as DBExpenseRepo

DUMMY_ID = 12345
DATABASE_URL = "sqlite:///expenses.db"

engine = create_engine(DATABASE_URL)

# Force the immediate initialization of the physical SQLite database and tables
SQLModel.metadata.create_all(engine)


def get_db_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session


def get_expense_repo(session: Session = Depends(get_db_session)) -> DBExpenseRepo:
    return DBExpenseRepo(session=session, db_url=DATABASE_URL)


def get_user_id(
    x_user_id: int | None = Header(default=None, alias="X-User-ID"),
    user_id: int | None = Query(default=None),
) -> int:
    """
    Resolves the target user ID. Extracts from HTTP Header primarily,
    falling back to query strings for Streamlit/Swagger UI cross-compatibility.
    """
    if x_user_id is not None:
        return x_user_id
    if user_id is not None:
        return user_id
    return DUMMY_ID
