from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class SQLiteEngineeringRepository:
    """
    Source-specific repository.

    This class knows how to read the synthetic SQLite
    engineering database but does not construct domain
    objects or perform business transformations.
    """

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)

        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found: {self.db_path}"
            )

    def _connect(self):
        connection = sqlite3.connect(
            self.db_path
        )

        connection.row_factory = sqlite3.Row

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection

    def get_entities(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    uid,
                    component_type,
                    discipline,
                    geometry_type,
                    x,
                    y,
                    width,
                    height,
                    rotation,
                    x1,
                    y1,
                    x2,
                    y2,
                    zone
                FROM spatial_entities
                ORDER BY uid
                """
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def get_attributes(
        self,
    ) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    rowid AS insertion_order,
                    uid,
                    attribute_name,
                    attribute_value
                FROM eav_attributes
                ORDER BY rowid
                """
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def get_connections(
        self,
    ) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    source_uid,
                    target_uid,
                    connection_type
                FROM component_connections
                ORDER BY source_uid, target_uid
                """
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def get_component(
        self,
        uid: str,
    ) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    uid,
                    component_type,
                    discipline,
                    geometry_type,
                    x,
                    y,
                    width,
                    height,
                    rotation,
                    x1,
                    y1,
                    x2,
                    y2,
                    zone
                FROM spatial_entities
                WHERE uid = ?
                """,
                (uid,),
            ).fetchone()

        if row is None:
            return None

        return dict(row)

    def get_attribute_rows(
        self,
        uid: str,
    ) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    rowid AS insertion_order,
                    uid,
                    attribute_name,
                    attribute_value
                FROM eav_attributes
                WHERE uid = ?
                ORDER BY rowid
                """,
                (uid,),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def get_component_connections(
        self,
        uid: str,
    ) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    source_uid,
                    target_uid,
                    connection_type
                FROM component_connections
                WHERE source_uid = ?
                   OR target_uid = ?
                ORDER BY source_uid, target_uid
                """,
                (uid, uid),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def count_entities(self) -> int:
        with self._connect() as conn:
            return conn.execute(
                """
                SELECT COUNT(*)
                FROM spatial_entities
                """
            ).fetchone()[0]

    def count_connections(self) -> int:
        with self._connect() as conn:
            return conn.execute(
                """
                SELECT COUNT(*)
                FROM component_connections
                """
            ).fetchone()[0]
