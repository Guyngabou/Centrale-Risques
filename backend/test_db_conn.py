import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Testing connection to: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        # Get tables for MSSQL
        tables_query = text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = connection.execute(tables_query).fetchall()
        print(f"Tables found: {[t[0] for t in tables]}")
        
        for table in tables:
            name = table[0]
            count_query = text(f'SELECT COUNT(*) FROM "{name}"')
            count = connection.execute(count_query).scalar()
            print(f"Table {name}: {count} rows")
            
except Exception as e:
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
