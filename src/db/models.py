from sqlalchemy import Column, String, Float, Date, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Price(Base):
    __tablename__ = "prices"

    ticker = Column(String, primary_key=True)
    date = Column(Date, primary_key=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volumn = Column(Float)