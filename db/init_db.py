from sqlalchemy import inspect, text

from db.models import Base
from db.session import engine

def add_missing_columns():
    """create_all() never alters existing tables, so add columns introduced after a table was created"""
    inspector = inspect(engine)
    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if not inspector.has_table(table.name):
                continue
            existing = {column['name'] for column in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name not in existing:
                    column_type = column.type.compile(dialect=engine.dialect)
                    conn.execute(text(f"ALTER TABLE {table.name} ADD {column.name} {column_type}"))
                    print(f"Added column {table.name}.{column.name}")

def init_database():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
    add_missing_columns()
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()
