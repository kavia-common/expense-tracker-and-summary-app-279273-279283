"""CLI-friendly database initialization and seed data utilities."""
from __future__ import annotations

import logging
from datetime import date

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.core.config import configure_logging
from src.db.session import db_session, engine
from src.db.base import Base
from src.models.models import Category, Transaction, User

logger = logging.getLogger(__name__)


# PUBLIC_INTERFACE
def init_db(create_schema: bool = True, seed: bool = True) -> None:
    """Initialize database schema and seed data.

    Args:
        create_schema: If True, create all tables if they don't exist.
        seed: If True, insert basic seed data if tables are empty.
    """
    configure_logging()
    if create_schema:
        Base.metadata.create_all(bind=engine)

    if not seed:
        return

    with db_session() as session:
        _seed(session)


def _seed(session: Session) -> None:
    """Insert default seed data idempotently."""
    try:
        # Check any existing users to avoid duplicating seed
        existing = session.query(User).count()
        if existing > 0:
            logger.info("Seed skipped: users already present")
            return

        # Create demo user
        user = User(email="demo@example.com", name="Demo User")
        session.add(user)
        session.flush()  # get user.id

        # Categories
        food = Category(name="Food", user_id=user.id)
        rent = Category(name="Rent", user_id=user.id)
        fun = Category(name="Entertainment", user_id=user.id)
        session.add_all([food, rent, fun])
        session.flush()

        # Transactions
        session.add_all(
            [
                Transaction(
                    user_id=user.id,
                    category_id=food.id,
                    amount=25.50,
                    currency="USD",
                    occurred_on=date.today(),
                    note="Lunch",
                ),
                Transaction(
                    user_id=user.id,
                    category_id=rent.id,
                    amount=1200.00,
                    currency="USD",
                    occurred_on=date.today().replace(day=1),
                    note="Monthly rent",
                ),
                Transaction(
                    user_id=user.id,
                    category_id=fun.id,
                    amount=45.00,
                    currency="USD",
                    occurred_on=date.today(),
                    note="Movie night",
                ),
            ]
        )
        logger.info("Database seeded with demo data.")
    except SQLAlchemyError as exc:
        logger.exception("Failed to seed database: %s", exc)
        raise
