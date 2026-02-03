import argparse
import os
from collections import defaultdict, deque
from datetime import date, datetime

from sqlalchemy import MetaData, create_engine, select, text


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migrate local SQLite data (agenda_scolaire.db) to Postgres (e.g. Supabase)."
    )
    parser.add_argument(
        "--sqlite-path",
        default="agenda_scolaire.db",
        help="Path to the SQLite database file (default: agenda_scolaire.db)",
    )
    parser.add_argument(
        "--postgres-url",
        default=os.environ.get("DATABASE_URL", ""),
        help="Destination Postgres DATABASE_URL (default: env DATABASE_URL)",
    )
    parser.add_argument(
        "--truncate-destination",
        action="store_true",
        help="DELETE all rows in destination tables before inserting.",
    )
    return parser.parse_args()


def _toposort_tables(table_deps: dict[str, set[str]]) -> list[str]:
    indegree: dict[str, int] = {t: 0 for t in table_deps}
    for t, deps in table_deps.items():
        for dep in deps:
            if dep in indegree:
                indegree[t] += 1

    queue = deque([t for t, d in indegree.items() if d == 0])
    order: list[str] = []

    reverse: dict[str, set[str]] = defaultdict(set)
    for t, deps in table_deps.items():
        for dep in deps:
            reverse[dep].add(t)

    while queue:
        t = queue.popleft()
        order.append(t)
        for child in reverse.get(t, set()):
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)

    # If cycles exist, append remaining tables (best-effort).
    remaining = [t for t in table_deps if t not in order]
    return order + remaining


def _coerce_value(value, dest_column) -> object:
    """Best-effort coercion from SQLite values to Postgres-compatible Python types."""
    if value is None:
        return None

    # SQLite may store dates/datetimes as strings.
    try:
        python_type = dest_column.type.python_type
    except Exception:
        python_type = None

    if python_type is datetime and isinstance(value, str):
        # Accept ISO strings like 2026-01-18T10:00:00 or 2026-01-18 10:00:00
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value

    if python_type is date and isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return value

    return value


def main() -> int:
    args = _parse_args()

    sqlite_path = args.sqlite_path
    postgres_url = (args.postgres_url or "").strip()

    if not os.path.exists(sqlite_path):
        raise SystemExit(f"SQLite file not found: {sqlite_path}")

    if not postgres_url:
        raise SystemExit(
            "Missing destination DATABASE_URL. Provide --postgres-url or set env DATABASE_URL."
        )

    if postgres_url.startswith("postgres://"):
        postgres_url = postgres_url.replace("postgres://", "postgresql://", 1)

    # Prevent app import from auto-creating tables (we control it explicitly).
    os.environ.setdefault("AUTO_INIT_DB", "false")
    os.environ["DATABASE_URL"] = postgres_url

    from app import app  # noqa: E402
    from models.user import db  # noqa: E402

    sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")

    # Reflect SQLite schema for reading.
    sqlite_md = MetaData()
    sqlite_md.reflect(bind=sqlite_engine)

    with app.app_context():
        pg_engine = db.engine

        # Ensure destination tables exist from models (keeps PK autoincrement behavior on Postgres).
        db.create_all()

        dest_tables = db.metadata.tables

        # Only migrate tables that exist both sides.
        common_table_names = [
            name for name in sqlite_md.tables.keys() if name in dest_tables
        ]

        if not common_table_names:
            raise SystemExit(
                "No common tables found between SQLite and destination models. "
                "Did you point to the right SQLite file?"
            )

        # Build dependency graph based on destination foreign keys.
        deps: dict[str, set[str]] = {name: set() for name in common_table_names}
        for name in common_table_names:
            table = dest_tables[name]
            for fk in table.foreign_keys:
                ref_table = fk.column.table.name
                if ref_table in deps and ref_table != name:
                    deps[name].add(ref_table)

        ordered = _toposort_tables(deps)

        with sqlite_engine.connect() as sqlite_conn, pg_engine.begin() as pg_conn:
            if args.truncate_destination:
                # Delete in reverse dependency order.
                for name in reversed(ordered):
                    pg_conn.execute(dest_tables[name].delete())

            for name in ordered:
                src = sqlite_md.tables.get(name)
                dest = dest_tables.get(name)
                if src is None or dest is None:
                    continue

                src_rows = sqlite_conn.execute(select(src)).mappings().all()
                if not src_rows:
                    continue

                dest_col_names = set(dest.columns.keys())

                payload: list[dict] = []
                for row in src_rows:
                    item: dict = {}
                    for col in dest.columns:
                        if col.name in row and col.name in dest_col_names:
                            item[col.name] = _coerce_value(row[col.name], col)
                    payload.append(item)

                if payload:
                    pg_conn.execute(dest.insert(), payload)

            # Fix sequences for integer primary keys (common after explicit id inserts).
            for name in ordered:
                table = dest_tables.get(name)
                if table is None:
                    continue

                pk_cols = list(table.primary_key.columns)
                if len(pk_cols) != 1:
                    continue

                pk = pk_cols[0]
                # Only for integer-ish PKs.
                try:
                    if pk.type.python_type is not int:
                        continue
                except Exception:
                    continue

                seq_sql = text(
                    "SELECT pg_get_serial_sequence(:table_name, :col_name) AS seq"
                )
                seq = pg_conn.execute(
                    seq_sql,
                    {"table_name": table.name, "col_name": pk.name},
                ).scalar()

                if not seq:
                    continue

                max_id = pg_conn.execute(select(text(f"MAX({pk.name})"))
                                         .select_from(table)).scalar()
                if max_id is None:
                    continue

                pg_conn.execute(
                    text("SELECT setval(:seq, :value, true)"),
                    {"seq": seq, "value": int(max_id)},
                )

    print("Migration complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
