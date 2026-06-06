from decimal import Decimal
from unittest.mock import MagicMock, patch

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from expenses_ai_agent.api.deps import get_expense_repo, get_user_id
from expenses_ai_agent.api.routes.expenses import router
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.storage.models import Currency, ExpenseCategory

# Ensure test application routing boundaries are cleanly declared
app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestApiRoutesExpenseClassifyOnly:
    @patch("expenses_ai_agent.api.routes.expenses.ClassificationService")
    @patch("expenses_ai_agent.api.routes.expenses.config")
    def test_classify_only_endpoint_executes_entire_body_successfully(
        self, mock_config, mock_service_class
    ):
        """
        Happy Path: Exercises every line of classify_only
        by mocking config lookups and the internal service.
        """

        # 1. Setup mock returns for the decouple config calls inside the route
        def mock_config_side_effect(key, default=None):
            if key == "OPENAI_MODEL":
                return "gpt-4o-mini"
            if key == "OPENAI_API_KEY":
                return "mock-active-key"
            return default

        mock_config.side_effect = mock_config_side_effect

        # 2. Forge the target Pydantic object
        # that ClassificationService normally spits out
        mock_response_payload = ExpenseCategorizationResponse(
            category=ExpenseCategory.TRANSPORT,
            total_amount=Decimal("35.00"),
            currency=Currency.USD,
            confidence=0.98,
        )

        # Mirror the container interface: result.response maps to our payload
        mock_result_container = MagicMock()
        mock_result_container.response = mock_response_payload

        # 3. Attach the mocked chain to the ClassificationService class constructor
        mock_service_instance = mock_service_class.return_value
        mock_service_instance.classify.return_value = mock_result_container

        # 4. Wire in basic dependency wrappers
        # to satisfy the FastAPI route injection hooks
        mock_repo = MagicMock()
        app.dependency_overrides[get_expense_repo] = lambda: mock_repo
        app.dependency_overrides[get_user_id] = lambda: 12345

        # 5. Build input parameters matching ExpenseClassifyRequest schemas
        request_data = {"description": "Uber ride back home from the terminal"}

        # 6. Execute the route directly via the HTTP client
        response = client.post("/expenses/classify", json=request_data)

        # 7. Tear down overrides immediately
        app.dependency_overrides.clear()

        # ==========================================
        # VERIFICATION MATRICES
        # ==========================================
        assert response.status_code == status.HTTP_201_CREATED

        # Verify the output format parsed and returned
        # matches our service mock precisely
        data = response.json()
        assert data["category"] == ExpenseCategory.TRANSPORT
        assert data["total_amount"] == "35.00"
        assert data["currency"] == Currency.USD
        assert data["confidence"] == 0.98

        # Structural Verifications:
        # Validate the service layer was generated with our assistant
        mock_service_class.assert_called_once()
        mock_service_instance.classify.assert_called_once_with(
            "Uber ride back home from the terminal"
        )
