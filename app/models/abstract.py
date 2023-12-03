from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.db import Base


class CharityProjectDonationCommon(Base):
    """Определяет общие поля для моделей CharityProject и Donation."""
    __abstract__ = True
    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime(timezone=True), default=datetime.now)
    close_date = Column(DateTime)

    @hybrid_property
    def balance(self):
        return self.full_amount - self.invested_amount
