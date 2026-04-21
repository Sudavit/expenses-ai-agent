from abc import ABC, abstractmethod

from expenses_ai_agent.storage.models import Expense, ExpenseCategory


class ExpenseRepository[T](ABC):
    @abstractmethod
    def add(self, entity: T) -> None:
        """Add a new entity to the repository."""
        ...

    @abstractmethod
    def get(self, id: int) -> T | None:
        """Read an entity from the repository."""
        ...

    @abstractmethod
    def get_all(self) -> list[T] | None:
        """Get all entities from the repository."""
        ...

    @abstractmethod
    def delete(self, entity: T) -> None:
        """Delete an entity from the repository."""
        ...

    @abstractmethod
    def search_by_category(self, category: ExpenseCategory) -> list[T] | None:
        """Search repository for a category."""
        ...


class InMemoryExpenseRepository(ExpenseRepository[Expense]):
    def add(self, entity: Expense) -> None:
        """Add a new entity to the repository."""
        pass

    def get(self, id: int) -> Expense | None:
        """Read an entity from the repository."""
        pass

    def get_all(self) -> list[Expense] | None:
        """Get all entities from the repository."""
        pass

    def delete(self, entity: Expense) -> None:
        """Delete an entity from the repository."""
        pass

    def search_by_category(self, category: ExpenseCategory) -> list[Expense] | None:
        """Search repository for a category."""
        pass
