from abc import ABC, abstractmethod

from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError
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
    def update(self, id: int, entity: T) -> None: ...

    @abstractmethod
    def delete(self, id: int) -> None:
        """Delete an entity from the repository."""
        ...

    @abstractmethod
    def search_by_category(self, category: ExpenseCategory) -> list[T]:
        """Search repository for a category."""
        ...


class InMemoryExpenseRepository(ExpenseRepository[Expense]):
    """
    InMemoryExpenseRepository is an in-memory data layer implemented as a dict.
    The basic CRUD operations are supported,
    as are get_all(), which retrieves all Expense items as a list,
    and search_by_category(), which looks for all elements
    with a specific ExpenseCategory

    Once created, objects remain in the database until deleted.
    The Create operation, add(), gives every new object put into the database a new ID.
    IDs start at 1, and increment by 1 for every subsequent object.
    No operations change IDs of objects in the database, once they're persisted.
    For example, update(), changes the internal data of an existing object,
    but keeps the original ID.

    This class, a "Fake" database, allows fast unit tests of my code with real results,
    without the setup and maintenance costs
    of an industrial-strength database like SQLModel.
    The price of an in-memory model is impermanence: no data persist across runs.

    Because it's written as a child of an ABC, it lets me use a repository pattern,
    which keeps the database implementation details
    from intruding into the rest of the code
    """

    def __init__(self):
        self.repo: dict[int, Expense] = dict()
        self.index: int = 0

    def _unique_id(self):
        self.index += 1
        return self.index

    def add(self, entity: Expense) -> None:
        """Add a new entity to the repository."""
        entity.id = self._unique_id()
        self.repo[entity.id] = entity

    def get(self, id: int) -> Expense | None:
        """Read an entity from the repository."""
        if id not in self.repo:
            return None
        return self.repo[id]

    def get_all(self) -> list[Expense]:
        """Get all entities from the repository."""
        return list(self.repo.values())

    def update(self, id: int, entity: Expense) -> None:
        if id not in self.repo:
            raise ExpenseNotFoundError(id)
        entity.id = id
        self.repo[entity.id] = entity

    def delete(self, id: int) -> None:
        """Delete an entity from the repository."""
        if id not in self.repo:
            raise ExpenseNotFoundError(id)
        del self.repo[id]

    def search_by_category(self, category: ExpenseCategory) -> list[Expense]:
        """Search repository for a category."""
        result = [
            expense for expense in self.repo.values() if expense.category == category
        ]
        return result
