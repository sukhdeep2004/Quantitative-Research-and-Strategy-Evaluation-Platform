from sqlalchemy import Column, Integer, Float, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MarketData(Base):
    __tablename__ = "market_data"
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    price = Column(Float)
    returns = Column(Float)
 