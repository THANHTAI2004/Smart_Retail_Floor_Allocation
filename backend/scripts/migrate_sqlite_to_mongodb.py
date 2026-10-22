"""Offline migration entry point; never imports SQLAlchemy or modifies SQLite."""

from smart_retail.infrastructure.mongodb.migration import main

if __name__ == "__main__":
    main()
