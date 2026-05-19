from collections.abc import Generator

from fastapi import Depends, Header
from sqlmodel import Session, create_engine

from expenses_ai_agent.storage.repo import DBExpenseRepository as DBExpenseRepo

DUMMY_ID = 12345

engine = create_engine("sqlite:///expenses.db")


def get_db_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session


def get_expense_repo(session: Session = Depends(get_db_session)) -> DBExpenseRepo:
    return DBExpenseRepo(session=session, db_url="sqlite:///expenses.db")


def get_user_id(
    x_user_id: int | None = Header(default=None, alias="X-User-ID"),
) -> int:
    if x_user_id:
        return x_user_id
    return DUMMY_ID
