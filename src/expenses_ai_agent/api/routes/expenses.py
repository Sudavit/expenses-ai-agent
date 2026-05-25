from decouple import config
from fastapi import APIRouter, Depends, HTTPException, status

from expenses_ai_agent.api.deps import get_expense_repo, get_user_id
from expenses_ai_agent.api.schemas.expense import (
    ExpenseClassifyRequest,
    ExpenseListResponse,
    ExpenseResponse,
)
from expenses_ai_agent.llms.openai import OpenAIAssistant
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.services.classification import ClassificationService
from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError
from expenses_ai_agent.storage.models import Expense
from expenses_ai_agent.storage.repo import ExpenseRepository

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("/", response_model=ExpenseListResponse)
def list_expenses(
    page: int = 1,
    page_size: int = 20,
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
    user_id: int = Depends(get_user_id),
) -> ExpenseListResponse:
    expenses = expense_repo.list_by_user(user_id)
    start = (page - 1) * page_size
    end = start + page_size
    sliced_expenses = expenses[start:end]

    items = [ExpenseResponse.model_validate(e) for e in sliced_expenses]

    return ExpenseListResponse(
        items=items,
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
    except ExpenseNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id {expense_id} not found",
        )
    return ExpenseResponse.model_validate(expense)


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_data: ExpenseResponse,
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
    user_id: int = Depends(get_user_id),
) -> ExpenseResponse:
    db_expense = Expense(
        amount=expense_data.amount,
        currency=expense_data.currency,
        date=expense_data.date,
        description=expense_data.description,
        telegram_user_id=user_id,
        category=expense_data.category,
    )
    expense_repo.add(db_expense)
    return ExpenseResponse.model_validate(db_expense)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_one_expense(
    expense_id: int,
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
    user_id: int = Depends(get_user_id),
) -> None:
    try:
        expense_repo.delete(expense_id)
    except ExpenseNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id {expense_id} not found",
        )


@router.post(
    "/classify",
    response_model=ExpenseCategorizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def classify(
    request: ExpenseClassifyRequest,
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
    user_id: int = Depends(get_user_id),
) -> ExpenseCategorizationResponse:
    model = config("OPENAI_MODEL", default="gpt-4o-mini")
    api_key = config("OPENAI_API_KEY", default="")

    assistant = OpenAIAssistant(model=model, api_key=api_key)
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
