# src/expenses_ai_agent/api/routes/analytics.py
from fastapi import APIRouter, Depends

from expenses_ai_agent.api.deps import get_expense_repo, get_user_id
from expenses_ai_agent.storage.models import ExpenseCategory
from expenses_ai_agent.storage.repo import ExpenseRepository

# The prefix here handles "/analytics"
router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/")
def get_summary(
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
    user_id: int = Depends(get_user_id),
) -> list[str]:

    return [category for category in ExpenseCategory]
