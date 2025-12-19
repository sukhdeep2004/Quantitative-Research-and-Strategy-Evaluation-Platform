import os
from dotenv import load_dotenv

load_dotenv()
URL= "mssql+pyodbc://quantadmin:Neeru#1983@quantadmin.database.windows.net:1433/quantdb?driver=ODBC+Driver+18+for+SQL+Server"

DATABASE_URL = os.getenv("DATABASE_URL", URL)

