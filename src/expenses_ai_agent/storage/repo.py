from abc import ABC, abstractmethod
from datetime import datetime

from sqlmodel import Session, SQLModel, create_engine, select

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
    def get_all(self) -> list[T]:
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

    @abstractmethod
    def search_by_dates(self, start: datetime, end: datetime) -> list[T]: ...

    @abstractmethod
    def list_by_user(self, telegram_user_id: int) -> list[T]: ...


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

    def search_by_dates(self, start: datetime, end: datetime) -> list[Expense]:
        """Search repository for expenses between a pair of dates."""
        result = [
            expense for expense in self.repo.values() if start <= expense.date <= end
        ]
        return result

    def list_by_user(self, telegram_user_id: int) -> list[Expense]:
        """Search repository for expenses by a particular user."""
        result = [
            expense
            for expense in self.repo.values()
            if expense.telegram_user_id == telegram_user_id
        ]
        return result


class DBExpenseRepository(ExpenseRepository[Expense]):
    """
    Persistent SQLModel-backed implementation of `ExpenseRepository`.

    Owns its session by default (constructor creates engine + session and
    schema), or accepts an externally managed session for testing/transactional
    contexts. Can be used as a context manager to guarantee cleanup of
    owned sessions.
    """

    def __init__(self, db_url: str, session: Session | None = None):
        self._db_url = db_url
        if session:
            self._session = session
            self._owns_session = False  # External session, don't close it
        else:
            engine = create_engine(db_url)
            SQLModel.metadata.create_all(engine)
            self._session = Session(engine)
            self._owns_session = True

    def close(self) -> None:
        """Close the database session if we own it."""
        if self._owns_session and self._session:
            self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def add(self, entity: Expense) -> None:
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)

    def get(self, id: int) -> Expense | None:
        return self._session.get(Expense, id)

    def get_all(self) -> list[Expense]:
        statement = select(Expense)
        return list(self._session.exec(statement))

    def update(self, id: int, entity: Expense) -> None:
        if not self.get(id):
            raise ExpenseNotFoundError(id)
        entity.id = id
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)

    def delete(self, id: int) -> None:
        expense = self.get(id)
        if not expense:
            raise ExpenseNotFoundError(id)
        self._session.delete(expense)
        self._session.commit()

    def search_by_category(self, category: ExpenseCategory) -> list[Expense]:
        statement = select(Expense).where(Expense.category == category)
        return list(self._session.exec(statement))

    def search_by_dates(self, start: datetime, end: datetime) -> list[Expense]:
        """Search repository for expenses between a pair of dates."""
        statement = select(Expense).where(Expense.date >= start, Expense.date <= end)
        return list(self._session.exec(statement))

    def list_by_user(self, telegram_user_id: int) -> list[Expense]:
        """Search repository for expenses by a particular user."""
        statement = select(Expense).where(Expense.telegram_user_id == telegram_user_id)
        return list(self._session.exec(statement))
