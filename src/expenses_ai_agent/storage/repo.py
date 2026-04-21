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
    """
    Implement `InMemoryExpenseRepository` backed by a `dict[int, Expense]`.
    The `add()` method assigns an auto-incrementing ID
     by mutating `expense.id` on the passed-in object
     — this mirrors how SQLAlchemy works:
        `session.add(obj)` + `session.commit()` sets the ID on the original object too.
    """

    def __init__(self):
        self.repo: dict[int, Expense] = dict()
        self.index: int = 0

    def add(self, entity: Expense) -> None:
        """Add a new entity to the repository."""
        self.index += 1
        entity.id = self.index
        self.repo[self.index] = entity

    def get(self, id: int) -> Expense | None:
        """Read an entity from the repository."""
        if id not in self.repo:
            return None
        return self.repo[id]

    def get_all(self) -> list[Expense] | None:
        """Get all entities from the repository."""
        all = list(self.repo.values())
        if all:
            return all
        else:
            return None

    def delete(self, entity: Expense) -> None:
        """Delete an entity from the repository."""
        self.repo = {
            id: expense for id, expense in self.repo.items() if expense != entity
        }

    def search_by_category(self, category: ExpenseCategory) -> list[Expense] | None:
        result = [
            expense for id, expense in self.repo.items() if expense.category == category
        ]
        """Search repository for a category."""
        return result
