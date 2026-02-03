import os

# Force DB init when running this script explicitly.
os.environ.setdefault("AUTO_INIT_DB", "true")

from app import _init_db_if_needed  # noqa: E402


if __name__ == "__main__":
    _init_db_if_needed()
    print("Database initialized (tables created).")
