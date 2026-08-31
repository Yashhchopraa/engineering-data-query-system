import json
import sqlite3
import time
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "generated" / "engineering_system.db"
RESULTS_DIR = PROJECT_ROOT / "data" / "results"

FULL_TABLE_PATH = RESULTS_DIR / "transformed_feature_table.csv"
SAMPLE_PATH = RESULTS_DIR / "transformed_feature_sample.csv"
SUMMARY_PATH = RESULTS_DIR / "transformation_summary.json"


def main():
    start_time = time.perf_counter()

    print("=" * 60)
    print("Engineering EAV Transformation Engine")
    print("=" * 60)
    print()
    print(f"Database: {DB_PATH}")
    print()

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}\n"
            "Run generate_data.py first."
        )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading SQLite data...")

    with sqlite3.connect(DB_PATH) as conn:

        entities = pd.read_sql_query(
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
            """,
            conn,
        )

        eav = pd.read_sql_query(
            """
            SELECT
                rowid AS insertion_order,
                uid,
                attribute_name,
                attribute_value
            FROM eav_attributes
            ORDER BY insertion_order
            """,
            conn,
        )

    print(
        f"Loaded {len(entities):,} entities "
        f"and {len(eav):,} EAV rows."
    )
    print()

    raw_eav_rows = len(eav)
    unique_attributes = eav["attribute_name"].nunique()

    print("Detecting and resolving duplicate attributes...")

    duplicate_groups = (
        eav.groupby(["uid", "attribute_name"])
        .size()
        .reset_index(name="occurrences")
    )

    duplicate_cases = duplicate_groups[
        duplicate_groups["occurrences"] > 1
    ]

    duplicate_case_count = len(duplicate_cases)

    duplicate_records_involved = (
        duplicate_cases["occurrences"].sum()
        if duplicate_case_count > 0
        else 0
    )

    eav_clean = (
        eav.sort_values("insertion_order")
        .drop_duplicates(
            subset=["uid", "attribute_name"],
            keep="first",
        )
    )

    cleaned_eav_rows = len(eav_clean)

    print("Pivoting EAV attributes into feature columns...")

    features = (
        eav_clean.pivot(
            index="uid",
            columns="attribute_name",
            values="attribute_value",
        )
        .reset_index()
    )

    features.columns.name = None

    attribute_columns = [
        column
        for column in features.columns
        if column != "uid"
    ]

    print("Merging spatial and component data...")

    feature_table = entities.merge(
        features,
        on="uid",
        how="left",
    )

    feature_table = feature_table.sort_values("uid").reset_index(drop=True)

    total_columns = len(feature_table.columns)

    feature_table.to_csv(
        FULL_TABLE_PATH,
        index=False,
    )

    feature_table.head(20).to_csv(
        SAMPLE_PATH,
        index=False,
    )

    elapsed = time.perf_counter() - start_time

    summary = {
        "input": {
            "spatial_entities": int(len(entities)),
            "raw_eav_rows": int(raw_eav_rows),
            "unique_attributes": int(unique_attributes),
        },
        "duplicate_resolution": {
            "duplicate_uid_attribute_cases": int(duplicate_case_count),
            "duplicate_eav_records_involved": int(
                duplicate_records_involved
            ),
            "eav_rows_after_cleaning": int(cleaned_eav_rows),
            "resolution_strategy": "Keep earliest inserted value",
        },
        "flattened_feature_table": {
            "rows": int(len(feature_table)),
            "columns": int(total_columns),
            "attribute_columns": int(len(attribute_columns)),
        },
        "output_files": {
            "full_feature_table": str(FULL_TABLE_PATH),
            "feature_sample": str(SAMPLE_PATH),
        },
        "transformation_time_seconds": round(elapsed, 6),
    }

    with open(SUMMARY_PATH, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)

    print()
    print("=" * 60)
    print("EAV Transformation Summary")
    print("=" * 60)
    print()

    print("Input Data")
    print("-" * 40)
    print(f"Spatial entities:       {len(entities):,}")
    print(f"Raw EAV rows:           {raw_eav_rows:,}")
    print(f"Unique attributes:      {unique_attributes:,}")
    print()

    print("Duplicate Resolution")
    print("-" * 40)
    print(
        f"Duplicate UID/attribute cases: "
        f"{duplicate_case_count:,}"
    )
    print(
        f"Duplicate EAV records involved: "
        f"{duplicate_records_involved:,}"
    )
    print(
        f"EAV rows after cleaning:        "
        f"{cleaned_eav_rows:,}"
    )
    print(
        "Resolution strategy:             "
        "Keep earliest inserted value"
    )
    print()

    print("Flattened Feature Table")
    print("-" * 40)
    print(f"Rows:                    {len(feature_table):,}")
    print(f"Columns:                 {total_columns:,}")
    print(f"Attribute columns:       {len(attribute_columns):,}")
    print()

    print("Transformation Time")
    print("-" * 40)
    print(f"Total transformation time: {elapsed:.6f} seconds")
    print()

    print("=" * 60)
    print("Outputs")
    print("-" * 40)
    print(f"Full feature table: {FULL_TABLE_PATH}")
    print(f"Feature sample:     {SAMPLE_PATH}")
    print(f"Summary:            {SUMMARY_PATH}")
    print()
    print("Transformation Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
