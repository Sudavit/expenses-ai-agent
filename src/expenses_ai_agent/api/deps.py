from typing import TYPE_CHECKING

from fastapi import Depends, Header
from sqlmodel import SQLModel

from expenses_ai_agent.storage.repo import DBExpenseRepository as DBExpenseRepo

if TYPE_CHECKING:

    def get_db_session() -> SQLModel: ...

    def get_expense_repo(session=Depends(get_db_session)) -> DBExpenseRepo: ...

    def get_user_id(
        x_user_id: int | None = Header(default=None, alias="X-User-ID"),
    ) -> int: ...
