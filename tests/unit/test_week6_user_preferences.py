from sqlmodel import create_engine, Session, SQLModel
from expenses_ai_agent.storage.models import Currency, UserPreference
from expenses_ai_agent.storage.repo import DBUserPreferenceRepo


class TestDBUserPreferenceRepo:
    """Targeted validation suite to guarantee 100% full coverage across DBUserPreferenceRepo."""

    def test_user_preference_lifecycle_inserts_and_updates_successfully(self):
        """Test initialization, get_by_user_id, and both branches of the upsert operation."""
        # 1. Spin up an isolated, structural memory sandbox engine
        engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(engine)

        with Session(engine) as session:
            # 2. Instantiate our repo layer injecting our shared active transaction channel
            repo = DBUserPreferenceRepo(db_url="sqlite:///:memory:", session=session)
            test_user_id = 444555

            # =================================================================
            # BRANCH A: Cold Upsert (The Insert Statement Path)
            # =================================================================
            # Initial search should return None
            initial_check = repo.get_by_user_id(test_user_id)
            assert initial_check is None

            # Trigger the insert block branch inside upsert()
            inserted_pref = repo.upsert(
                telegram_user_id=test_user_id, currency=Currency.EUR
            )

            assert inserted_pref.telegram_user_id == test_user_id
            assert inserted_pref.preferred_currency == Currency.EUR

            # Confirm database visibility immediately following refresh operations
            lookup_check = repo.get_by_user_id(test_user_id)
            assert lookup_check is not None
            assert lookup_check.preferred_currency == Currency.EUR

            # =================================================================
            # BRANCH B: Hot Upsert (The Update Mutation Path)
            # =================================================================
            # Trigger the update statement branch by changing the active user choice
            updated_pref = repo.upsert(
                telegram_user_id=test_user_id, currency=Currency.USD
            )

            assert updated_pref.telegram_user_id == test_user_id
            assert updated_pref.preferred_currency == Currency.USD

            # Re-fetch from scratch to verify modification persistency properties
            final_lookup = repo.get_by_user_id(test_user_id)
            assert final_lookup is not None
            assert final_lookup.preferred_currency == Currency.USD

    def test_constructor_initialization_without_managed_session(self):
        """Happy Path: Exercises the session=None branch of the constructor initialization process."""
        # This executes the inner conditional lines 3-6 of the class setup layout
        repo = DBUserPreferenceRepo(db_url="sqlite:///:memory:")
        assert repo.db is not None

        # Explicit session resource release management safely following validation tracking
        repo.db.close()
