from fastapi import APIRouter, Depends

from expenses_ai_agent.api.deps import get_expense_repo, get_user_id
from expenses_ai_agent.api.schemas.expense import (
    ExpenseClassifyRequest,
    ExpenseClassifyResponse,
    ExpenseListResponse,
    ExpenseResponse,
)
from expenses_ai_agent.llms.openai import OpenAIAssistant
from expenses_ai_agent.services.classification import ClassificationService
from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError
from expenses_ai_agent.storage.repo import ExpenseRepository

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("/", response_model=ExpenseListResponse)
def list_expenses(
    page: int = 1,
    page_size: int = 20,
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
    user_id: int = Depends(get_user_id),
) -> None:
    expenses = expense_repo.list_by_user(user_id)
    start = (page - 1) * page_size
    end = start + page_size
    return ExpenseListResponse(
        items=expenses[start:end],
        total=len(expenses),
        page=page,
        page_size=page_size,
    )


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_one_expense(
    expense_id: int,
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
    user_id: int = Depends(get_user_id),
) -> ExpenseResponse:
    try:
        expense = expense_repo.get(expense_id)
    except ExpenseNotFoundError("HTTP 404"):
        raise ExpenseNotFoundError("HTTP 404")  # TODO: This can't be right

    return expense


@router.delete("/{expense_id}")
def delete_one_expense(
    expense_id: int,
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
    user_id: int = Depends(get_user_id),
) -> int:
    expense_repo.delete(expense_id)
    return 204
    # TODO: return 204, somehow


@router.post("/classify", response_model=ExpenseClassifyResponse)
def classify(
    request: ExpenseClassifyRequest,
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
    user_id: int = Depends(get_user_id),
) -> ExpenseClassifyResponse:
    assistant = OpenAIAssistant(...)  # TODO: fill in args
    result = ClassificationService(
        assistant=assistant, expense_repo=expense_repo
    ).classify(request.description)
    return result.response


"""
GET /expenses/ — returns ExpenseListResponse; call repo.list_by_user(user_id)
GET /expenses/{id} — returns ExpenseResponse; call repo.get(expense_id)
    (integer only, no user_id);
    wrap in try/except ExpenseNotFoundError and raise HTTP 404
    — the repo raises, it does not return None
DELETE /expenses/{id} — returns 204; call repo.delete(expense_id)
    with the integer only (no user_id)
POST /expenses/classify — construct an Assistant instance (e.g. OpenAIAssistant(...))
    and pass it as the required first argument:
    ClassificationService(assistant=assistant, expense_repo=repo).classify(request.description);
    it returns a ClassificationResult with a .response attribute (ExpenseCategorizationResponse);
    return result.response directly using response_model=ExpenseCategorizationResponse;
    do not call any repo method here
"""  # noqa: E501
