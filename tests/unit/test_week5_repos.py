from datetime import UTC, datetime, timedelta
from decimal import Decimal

from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory
from expenses_ai_agent.storage.repo import (
    DBExpenseRepository,
    InMemoryExpenseRepository,
)


class TestInMemoryRepoSummaries:
    """
    Test uncovered aggregation methods in InMemoryExpenseRepository.
    """

    def test_search_by_dates_covers_date_range_filtering(self):
        """Exercises search_by_dates by tracking matching boundaries."""
        repo = InMemoryExpenseRepository()
        base_time = datetime(2026, 6, 1, 12, 0, 0, tzinfo=UTC)

        expense_target = Expense(
            amount=Decimal("15.50"),
            currency=Currency.EUR,
            date=base_time,
            description="Target Lunch",
            category=ExpenseCategory.FOOD,
            telegram_user_id=111,
        )
        expense_outside = Expense(
            amount=Decimal("50.00"),
            currency=Currency.EUR,
            date=base_time + timedelta(days=10),
            description="Outside Window",
            category=ExpenseCategory.TRANSPORT,
            telegram_user_id=111,
        )

        repo.add(expense_target)
        repo.add(expense_outside)

        # Trigger search_by_dates completely
        results = repo.search_by_dates(
            base_time - timedelta(days=1), base_time + timedelta(days=1)
        )

        assert len(results) == 1
        assert results[0].description == "Target Lunch"

    def test_list_by_user_covers_ownership_filtering(self):
        """Exercises list_by_user to ensure accurate identification across users."""
        repo = InMemoryExpenseRepository()
        base_time = datetime(2026, 6, 1, 12, 0, 0, tzinfo=UTC)

        user_a_expense = Expense(
            amount=Decimal("20.00"),
            currency=Currency.USD,
            date=base_time,
            description="User A Item",
            category=ExpenseCategory.TRANSPORT,
            telegram_user_id=12345,
        )
        user_b_expense = Expense(
            amount=Decimal("30.00"),
            currency=Currency.USD,
            date=base_time,
            description="User B Item",
            category=ExpenseCategory.FOOD,
            telegram_user_id=67890,
        )

        repo.add(user_a_expense)
        repo.add(user_b_expense)

        # Trigger list_by_user completely
        results = repo.list_by_user(12345)

        assert len(results) == 1
        assert results[0].description == "User A Item"

    def test_get_monthly_totals_calculates_accurate_time_aggregations(self):
        """
        Exercises get_monthly_totals
        to guarantee date-string dictionary sorting logic.
        """
        repo = InMemoryExpenseRepository()
        user_id = 99999

        # Target month elements
        repo.add(
            Expense(
                amount=Decimal("10.00"),
                currency=Currency.EUR,
                date=datetime(2026, 6, 5, 10, 0, tzinfo=UTC),
                description="Coffee 1",
                category=ExpenseCategory.FOOD,
                telegram_user_id=user_id,
            )
        )
        repo.add(
            Expense(
                amount=Decimal("25.50"),
                currency=Currency.EUR,
                date=datetime(2026, 6, 20, 15, 0, tzinfo=UTC),
                description="Dinner",
                category=ExpenseCategory.FOOD,
                telegram_user_id=user_id,
            )
        )
        # Different month element
        repo.add(
            Expense(
                amount=Decimal("100.00"),
                currency=Currency.EUR,
                date=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
                description="Next Month Hotel",
                category=ExpenseCategory.OTHER,
                telegram_user_id=user_id,
            )
        )

        # Trigger get_monthly_totals completely
        totals = repo.get_monthly_totals(user_id)

        # Verify month groupings combine and calculate correctly
        assert totals["2026-06"] == Decimal("35.50")
        assert totals["2026-07"] == Decimal("100.00")

    def test_get_category_totals_calculates_accurate_enum_aggregations(self):
        """
        Exercises get_category_totals
        to verify categorical grouping iteration pipelines.
        """
        repo = InMemoryExpenseRepository()
        user_id = 88888

        repo.add(
            Expense(
                amount=Decimal("45.00"),
                currency=Currency.USD,
                date=datetime.now(UTC),
                description="Weekly Groceries",
                category=ExpenseCategory.FOOD,
                telegram_user_id=user_id,
            )
        )
        repo.add(
            Expense(
                amount=Decimal("15.00"),
                currency=Currency.USD,
                date=datetime.now(UTC),
                description="Train Ticket",
                category=ExpenseCategory.TRANSPORT,
                telegram_user_id=user_id,
            )
        )

        # Trigger get_category_totals completely
        totals = repo.get_category_totals(user_id)

        # Verify enum keys accumulate value mappings correctly
        assert totals[ExpenseCategory.FOOD] == Decimal("45.00")
        assert totals[ExpenseCategory.TRANSPORT] == Decimal("15.00")


class TestDBRepoSummaries:
    """Test database aggregation methods in DBExpenseRepository."""

    def test_db_get_monthly_totals_calculates_accurate_aggregations(self):
        """
        Verifies SQLModel reads, aggregates, and transforms date objects
        to monthly strings.
        """
        # 1. Initialize the repository with isolated, in-memory SQLite sandbox database
        with DBExpenseRepository("sqlite:///:memory:") as repo:
            user_id = 77711

            # 2. Add realistic records directly to the database instance context
            repo.add(
                Expense(
                    amount=Decimal("12.50"),
                    currency=Currency.EUR,
                    date=datetime(2026, 6, 5, 10, 0, tzinfo=UTC),
                    description="Lunch snack",
                    category=ExpenseCategory.FOOD,
                    telegram_user_id=user_id,
                )
            )
            repo.add(
                Expense(
                    amount=Decimal("40.00"),
                    currency=Currency.EUR,
                    date=datetime(2026, 6, 12, 18, 30, tzinfo=UTC),
                    description="Fuel fill",
                    category=ExpenseCategory.TRANSPORT,
                    telegram_user_id=user_id,
                )
            )
            repo.add(
                Expense(
                    amount=Decimal("150.00"),
                    currency=Currency.EUR,
                    date=datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
                    description="Train pass next month",
                    category=ExpenseCategory.TRANSPORT,
                    telegram_user_id=user_id,
                )
            )

            # 3. Trigger the database monthly total lookup method completely
            totals = repo.get_monthly_totals(user_id)

            # 4. Verify query engine groups timestamps
            # into accurate string bucket totals
            assert totals["2026-06"] == Decimal("52.50")
            assert totals["2026-07"] == Decimal("150.00")

    def test_db_get_category_totals_calculates_accurate_aggregations(self):
        """Verifies SQLModel pulls, filters, creates accurate category-enum totals."""
        with DBExpenseRepository("sqlite:///:memory:") as repo:
            user_id = 77722

            # 1. Insert records targeting multiple category enum choices
            repo.add(
                Expense(
                    amount=Decimal("35.00"),
                    currency=Currency.USD,
                    date=datetime.now(UTC),
                    description="Dinner date",
                    category=ExpenseCategory.FOOD,
                    telegram_user_id=user_id,
                )
            )
            repo.add(
                Expense(
                    amount=Decimal("15.00"),
                    currency=Currency.USD,
                    date=datetime.now(UTC),
                    description="App store utility",
                    category=ExpenseCategory.OTHER,
                    telegram_user_id=user_id,
                )
            )

            # 2. Trigger the database category total lookup method completely
            totals = repo.get_category_totals(user_id)

            # 3. Verify that the selection results correctly partition amounts by keys
            assert totals[ExpenseCategory.FOOD] == Decimal("35.00")
            assert totals[ExpenseCategory.OTHER] == Decimal("15.00")
