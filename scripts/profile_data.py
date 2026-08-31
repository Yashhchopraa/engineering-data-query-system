import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "generated" / "engineering_system.db"
OUTPUT_DIR = PROJECT_ROOT / "data" / "results"


def print_header(title):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def get_connection():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}\n"
            "Run generate_data.py first."
        )

    return sqlite3.connect(DB_PATH)


def profile_dataset():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    conn = get_connection()

    entities = pd.read_sql_query(
        "SELECT * FROM spatial_entities",
        conn
    )

    eav = pd.read_sql_query(
        "SELECT * FROM eav_attributes",
        conn
    )

    conn.close()

    print_header("Engineering Data Profiling Report")

    # --------------------------------------------------
    # 1. DATASET OVERVIEW
    # --------------------------------------------------

    print()
    print("Dataset Overview")
    print("-" * 40)

    overview = {
        "Spatial entities": len(entities),
        "EAV attribute rows": len(eav),
        "Disciplines": entities["discipline"].nunique(),
        "Component types": entities["component_type"].nunique(),
        "Unique attributes": eav["attribute_name"].nunique(),
    }

    for key, value in overview.items():
        print(f"{key:<25} {value:,}")

    overview_df = pd.DataFrame(
        list(overview.items()),
        columns=["Metric", "Value"]
    )

    overview_df.to_csv(
        OUTPUT_DIR / "dataset_overview.csv",
        index=False
    )

    # --------------------------------------------------
    # 2. DISCIPLINE DISTRIBUTION
    # --------------------------------------------------

    print()
    print("Discipline Distribution")
    print("-" * 40)

    discipline_distribution = (
        entities["discipline"]
        .value_counts()
        .rename_axis("discipline")
        .reset_index(name="component_count")
    )

    print(
        discipline_distribution.to_string(index=False)
    )

    discipline_distribution.to_csv(
        OUTPUT_DIR / "discipline_distribution.csv",
        index=False
    )

    # --------------------------------------------------
    # 3. COMPONENT TYPE DISTRIBUTION
    # --------------------------------------------------

    print()
    print("Component Type Distribution")
    print("-" * 40)

    component_distribution = (
        entities["component_type"]
        .value_counts()
        .rename_axis("component_type")
        .reset_index(name="component_count")
    )

    print(
        component_distribution.to_string(index=False)
    )

    component_distribution.to_csv(
        OUTPUT_DIR / "component_distribution.csv",
        index=False
    )

    # --------------------------------------------------
    # 4. ATTRIBUTE COVERAGE
    # --------------------------------------------------

    print()
    print("Attribute Coverage")
    print("-" * 40)

    attribute_coverage = (
        eav.groupby("attribute_name")["uid"]
        .nunique()
        .reset_index(name="entities_with_attribute")
    )

    total_entities = len(entities)

    attribute_coverage["coverage_percent"] = (
        attribute_coverage["entities_with_attribute"]
        / total_entities
        * 100
    )

    attribute_coverage["missing_entities"] = (
        total_entities
        - attribute_coverage["entities_with_attribute"]
    )

    attribute_coverage = attribute_coverage.sort_values(
        by="coverage_percent",
        ascending=False
    )

    print(
        attribute_coverage.to_string(
            index=False,
            formatters={
                "coverage_percent": "{:.2f}".format
            }
        )
    )

    attribute_coverage.to_csv(
        OUTPUT_DIR / "attribute_coverage.csv",
        index=False
    )

    # --------------------------------------------------
    # 5. DUPLICATE UID + ATTRIBUTE DETECTION
    # --------------------------------------------------

    print()
    print("Duplicate Attribute Analysis")
    print("-" * 40)

    duplicate_cases = (
        eav.groupby(["uid", "attribute_name"])
        .size()
        .reset_index(name="occurrences")
    )

    duplicate_cases = duplicate_cases[
        duplicate_cases["occurrences"] > 1
    ]

    print(
        f"Duplicate UID/attribute cases: "
        f"{len(duplicate_cases):,}"
    )

    if not duplicate_cases.empty:
        print()
        print(
            duplicate_cases.head(10).to_string(
                index=False
            )
        )

    duplicate_cases.to_csv(
        OUTPUT_DIR / "duplicate_attributes.csv",
        index=False
    )

    # --------------------------------------------------
    # 6. INVALID NUMERIC VALUE DETECTION
    # --------------------------------------------------

    print()
    print("Invalid Numeric Value Analysis")
    print("-" * 40)

    numeric_attributes = [
        "PressureRating_PSI",
        "Diameter_mm",
        "Capacity_m3h",
        "Voltage_V",
        "Airflow_m3h",
        "Length_m",
    ]

    invalid_numeric_rows = []

    for attribute in numeric_attributes:
        subset = eav[
            eav["attribute_name"] == attribute
        ].copy()

        if subset.empty:
            continue

        subset["numeric_value"] = pd.to_numeric(
            subset["attribute_value"],
            errors="coerce"
        )

        invalid = subset[
            (subset["numeric_value"].isna())
            | (subset["numeric_value"] < 0)
        ]

        if not invalid.empty:
            invalid_numeric_rows.append(invalid)

    if invalid_numeric_rows:
        invalid_numeric = pd.concat(
            invalid_numeric_rows,
            ignore_index=True
        )
    else:
        invalid_numeric = pd.DataFrame(
            columns=[
                "uid",
                "attribute_name",
                "attribute_value",
                "numeric_value",
            ]
        )

    print(
        f"Invalid numeric values detected: "
        f"{len(invalid_numeric):,}"
    )

    if not invalid_numeric.empty:
        print()
        print(
            invalid_numeric.head(10).to_string(
                index=False
            )
        )

    invalid_numeric.to_csv(
        OUTPUT_DIR / "invalid_numeric_values.csv",
        index=False
    )

    # --------------------------------------------------
    # 7. SCHEMA POLLUTION DETECTION
    # --------------------------------------------------

    print()
    print("Schema Pollution Analysis")
    print("-" * 40)

    known_attributes = {
        "Material",
        "Diameter_mm",
        "PressureRating_PSI",
        "Insulation",
        "FluidType",
        "Status",
        "Vendor",
        "EquipmentType",
        "Capacity_m3h",
        "Voltage_V",
        "Material_Grade",
        "SectionType",
        "Length_m",
        "Coating",
        "VoltageLevel",
        "IP_Rating",
        "DuctSize_mm",
        "Airflow_m3h",
        "PressureClass",
    }

    schema_pollution = eav[
        ~eav["attribute_name"].isin(
            known_attributes
        )
    ]

    print(
        f"Unexpected attribute records: "
        f"{len(schema_pollution):,}"
    )

    if not schema_pollution.empty:
        print()
        print(
            schema_pollution.head(10).to_string(
                index=False
            )
        )

    schema_pollution.to_csv(
        OUTPUT_DIR / "schema_pollution.csv",
        index=False
    )

    # --------------------------------------------------
    # 8. SUMMARY
    # --------------------------------------------------

    print_header("Profiling Summary")

    summary = {
        "Spatial entities": len(entities),
        "EAV rows": len(eav),
        "Unique attributes": eav["attribute_name"].nunique(),
        "Duplicate cases": len(duplicate_cases),
        "Invalid numeric values": len(invalid_numeric),
        "Schema pollution records": len(schema_pollution),
    }

    for key, value in summary.items():
        print(f"{key:<30} {value:,}")

    summary_df = pd.DataFrame(
        list(summary.items()),
        columns=["Metric", "Value"]
    )

    summary_df.to_csv(
        OUTPUT_DIR / "profiling_summary.csv",
        index=False
    )

    print()
    print("Profiling results saved to:")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    profile_dataset()
