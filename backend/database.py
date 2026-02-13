import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
from urllib.parse import quote_plus

username = "ngabou"
password = quote_plus("Guy_sys001")
host = "apsys.database.windows.net"
database = "RISQUESAGG"
driver = "pymssql"

SQLALCHEMY_DATABASE_URL = f"mssql+{driver}://{username}:{password}@{host}/{database}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
