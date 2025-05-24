import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

class DatabaseConnection:
    _connection_pool = None

    @classmethod
    def initialize_pool(cls):
        if cls._connection_pool is None:
            cls._connection_pool = pool.SimpleConnectionPool(
                1, 10,
                host=os.getenv('DB_HOST'),
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD')
            )

    @classmethod
    def get_connection(cls):
        if cls._connection_pool is None:
            cls.initialize_pool()
        return cls._connection_pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        cls._connection_pool.putconn(connection)

    @classmethod
    def close_all_connections(cls):
        if cls._connection_pool is not None:
            cls._connection_pool.closeall()

# Database connection string
DATABASE_URL = 'postgresql://postgres:Bahardb1234@localhost:5432/Olympicdb'

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def execute_query(query, params=None):
    """Execute a query and return the results as a list of dictionaries."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query), params or {})
            if result.returns_rows:
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result.fetchall()]
            return None
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close() 