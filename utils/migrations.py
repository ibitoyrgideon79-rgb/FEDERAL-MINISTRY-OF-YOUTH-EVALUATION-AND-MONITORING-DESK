from sqlalchemy import text
from sqlalchemy.engine import Engine


def _sqlite_has_column(engine: Engine, table_name: str, column_name: str) -> bool:
    with engine.connect() as conn:
        result = conn.execute(text(f"PRAGMA table_info({table_name})"))
        return any(row[1] == column_name for row in result)


def _postgres_has_column(engine: Engine, table_name: str, column_name: str) -> bool:
    query = text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name = :table AND column_name = :column"
    )
    with engine.connect() as conn:
        result = conn.execute(query, {"table": table_name, "column": column_name}).first()
        return result is not None


def ensure_programme_columns(engine: Engine, is_sqlite: bool):
    checks = _sqlite_has_column if is_sqlite else _postgres_has_column
    columns_to_add = [
        ("description", "TEXT"),
        ("recipient_email", "VARCHAR"),
    ]
    for column_name, column_type in columns_to_add:
        if not checks(engine, "programmes", column_name):
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE programmes ADD COLUMN {column_name} {column_type}"))
                conn.commit()
