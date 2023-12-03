from sqlalchemy import Column, String, Text

from app.models.abstract import CharityProjectDonationCommon


class CharityProject(CharityProjectDonationCommon):
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
