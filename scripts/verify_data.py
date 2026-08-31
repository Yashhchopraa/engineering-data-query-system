import sqlite3
from pathlib import Path


DB_PATH = Path(
    "data/generated/engineering_system.db"
)


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    print()
    print("=" * 60)
    print("Engineering Dataset Verification")
    print("=" * 60)

    entity_count = cursor.execute(
        """
        SELECT COUNT(*)
        FROM spatial_entities
        """
    ).fetchone()[0]

    eav_count = cursor.execute(
        """
        SELECT COUNT(*)
        FROM eav_attributes
        """
    ).fetchone()[0]

    orphan_count = cursor.execute(
        """
        SELECT COUNT(*)
        FROM eav_attributes a
        LEFT JOIN spatial_entities e
            ON a.uid = e.uid
        WHERE e.uid IS NULL
        """
    ).fetchone()[0]

    duplicate_cases = cursor.execute(
        """
        SELECT
            uid,
            attribute_name,
            COUNT(*) AS occurrences
        FROM eav_attributes
        GROUP BY uid, attribute_name
        HAVING COUNT(*) > 1
        """
    ).fetchall()

    invalid_pressure = cursor.execute(
        """
        SELECT
            uid,
            attribute_value
        FROM eav_attributes
        WHERE attribute_name = 'PressureRating_PSI'
          AND CAST(attribute_value AS REAL) < 0
        """
    ).fetchall()

    pollution_records = cursor.execute(
        """
        SELECT
            uid,
            attribute_name,
            attribute_value
        FROM eav_attributes
        WHERE attribute_name = 'ContaminatedPath'
        """
    ).fetchall()

    print()
    print("Database Counts")
    print("-" * 40)
    print(f"Spatial entities: {entity_count:,}")
    print(f"EAV rows:         {eav_count:,}")
    print(f"Orphan EAV rows:  {orphan_count:,}")

    print()
    print("Anomaly Verification")
    print("-" * 40)
    print(
        f"Duplicate UID/attribute cases: "
        f"{len(duplicate_cases):,}"
    )
    print(
        f"Invalid pressure values:        "
        f"{len(invalid_pressure):,}"
    )
    print(
        f"Schema pollution records:       "
        f"{len(pollution_records):,}"
    )

    print()
    print("Sample Duplicate Cases")
    print("-" * 40)

    for uid, attribute_name, occurrences in duplicate_cases[:5]:
        print(
            f"{uid} | "
            f"{attribute_name} | "
            f"{occurrences} occurrences"
        )

    print()
    print("Sample Entities")
    print("-" * 40)

    sample_entities = cursor.execute(
        """
        SELECT
            uid,
            component_type,
            discipline,
            x1,
            y1,
            x2,
            y2
        FROM spatial_entities
        ORDER BY uid
        LIMIT 5
        """
    ).fetchall()

    for entity in sample_entities:
        (
            uid,
            component_type,
            discipline,
            x1,
            y1,
            x2,
            y2
        ) = entity

        print()
        print(f"UID:        {uid}")
        print(f"Type:       {component_type}")
        print(f"Discipline: {discipline}")
        print(
            f"Bounds:     "
            f"({x1}, {y1}) -> ({x2}, {y2})"
        )

        attributes = cursor.execute(
            """
            SELECT
                attribute_name,
                attribute_value
            FROM eav_attributes
            WHERE uid = ?
            ORDER BY attribute_name
            """,
            (uid,)
        ).fetchall()

        for attribute_name, attribute_value in attributes:
            print(
                f"  - {attribute_name}: "
                f"{attribute_value}"
            )

    connection.close()

    print()
    print("=" * 60)
    print("Verification Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
