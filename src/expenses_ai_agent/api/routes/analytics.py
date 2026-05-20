# src/expenses_ai_agent/api/routes/analytics.py
from decimal import Decimal

from fastapi import APIRouter, Depends

from expenses_ai_agent.api.deps import get_expense_repo, get_user_id
from expenses_ai_agent.storage.repo import ExpenseRepository

# The prefix here handles "/analytics"
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=dict[str, dict[str, Decimal]])
def get_summary(
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
    user_id: int = Depends(get_user_id),
) -> dict[str, dict[str, Decimal]]:
    # Call your repo aggregates here...
    monthly_totals = expense_repo.get_monthly_totals(user_id)
    category_totals = expense_repo.get_category_totals(user_id)

    return {"category_totals": category_totals, "monthly_totals": monthly_totals}
