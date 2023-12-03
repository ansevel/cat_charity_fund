from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.abstract import CharityProjectDonationCommon


class Donation(CharityProjectDonationCommon):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)
