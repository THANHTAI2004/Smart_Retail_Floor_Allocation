"""SQLAlchemy persistence, shared by API and process worker."""

import os
from pathlib import Path

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    create_engine,
    event,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

ROOT = Path(os.getenv("SMART_RETAIL_HOME", str(Path.cwd()))).resolve()


class Base(DeclarativeBase):
    pass


class ProjectRecord(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    revision: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[str] = mapped_column(String(40))
    sections: Mapped[dict] = mapped_column(JSON, default=dict)


class ProductKey(Base):
    __tablename__ = "product_keys"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    sku: Mapped[str] = mapped_column(String(120), primary_key=True)


class OrderRecord(Base):
    __tablename__ = "orders"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    placed_at: Mapped[str] = mapped_column(String(50))
    kind: Mapped[str] = mapped_column(String(20))
    due_s: Mapped[float] = mapped_column(Float)
    __table_args__ = (CheckConstraint("due_s > 0"),)


class OrderLineRecord(Base):
    __tablename__ = "order_lines"
    project_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    order_id: Mapped[str] = mapped_column(String(120), primary_key=True)
    sku: Mapped[str] = mapped_column(String(120), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer)
    __table_args__ = (
        ForeignKeyConstraint(["project_id", "order_id"], ["orders.project_id", "orders.id"]),
        ForeignKeyConstraint(
            ["project_id", "sku"], ["product_keys.project_id", "product_keys.sku"]
        ),
        CheckConstraint("quantity > 0"),
    )


class RunRecord(Base):
    __tablename__ = "optimization_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    project_revision: Mapped[int] = mapped_column(Integer)
    input_sha256: Mapped[str] = mapped_column(String(64))
    snapshot: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(30), default="QUEUED", index=True)
    stage: Mapped[str] = mapped_column(String(20), default="PENDING")
    created_at: Mapped[str] = mapped_column(String(40))
    started_epoch: Mapped[float | None] = mapped_column(Float, nullable=True)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    result_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)


class WorkerHeartbeat(Base):
    __tablename__ = "worker_heartbeats"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    epoch: Mapped[float] = mapped_column(Float)


def database_url() -> str:
    default = ROOT / "var" / "smart_retail.db"
    return os.getenv("SMART_RETAIL_DATABASE_URL", f"sqlite:///{default.as_posix()}")


def connect(url: str | None = None):
    url = url or database_url()
    if url.startswith("sqlite"):
        (ROOT / "var").mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        url,
        connect_args={"check_same_thread": False, "timeout": 30}
        if url.startswith("sqlite")
        else {},
        pool_pre_ping=True,
    )
    if url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def setup(dbapi_connection, _):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

    return engine, sessionmaker(engine, expire_on_commit=False)
