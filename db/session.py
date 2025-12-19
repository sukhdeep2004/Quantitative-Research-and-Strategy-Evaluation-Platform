from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mssql+pyodbc://user:password@server/db?driver=ODBC+Driver+18+for+SQL+Server"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

