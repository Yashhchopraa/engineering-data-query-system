import sqlite3
import time
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "generated" / "engineering_system.db"
RESULTS_DIR = PROJECT_ROOT / "data" / "results"
FEATURE_TABLE_PATH = RESULTS_DIR / "transformed_feature_table.csv"


class EngineeringQueryEngine:
    """
    Provides two equivalent query mechanisms:

    1. Direct SQLite queries against the normalized EAV structure.
    2. Pandas queries against the flattened feature table.

    Both mechanisms use the same duplicate-resolution rule:
    keep the earliest inserted value for each
    (uid, attribute_name) pair.
    """

    def __init__(self):
        if not DB_PATH.exists():
            raise FileNotFoundError(
                f"Database not found: {DB_PATH}\n"
                "Run generate_data.py first."
            )

        if not FEATURE_TABLE_PATH.exists():
            raise FileNotFoundError(
                f"Feature table not found: {FEATURE_TABLE_PATH}\n"
                "Run transform_data.py first."
            )

        self.feature_table = None

    def load_feature_table(self):
        """Load the full flattened feature table."""
        print("Loading flattened feature table...")

        self.feature_table = pd.read_csv(
            FEATURE_TABLE_PATH,
            dtype=str,
        )

        print(
            f"Loaded {len(self.feature_table):,} rows "
            f"and {len(self.feature_table.columns):,} columns."
        )
        print()

    def query_sqlite(
        self,
        discipline=None,
        component_type=None,
        attributes=None,
    ):
        """
        Query the normalized SQLite EAV structure.

        attributes example:
        {
            "Material": "Carbon_Steel",
            "Status": "Installed"
        }
        """

        start_time = time.perf_counter()

        attributes = attributes or {}

        base_query = """
        WITH cleaned_eav AS (
            SELECT
                uid,
                attribute_name,
                attribute_value
            FROM (
                SELECT
                    rowid AS insertion_order,
                    uid,
                    attribute_name,
                    attribute_value,
                    ROW_NUMBER() OVER (
                        PARTITION BY uid, attribute_name
                        ORDER BY rowid
                    ) AS rn
                FROM eav_attributes
            )
            WHERE rn = 1
        )
        SELECT DISTINCT
            s.uid,
            s.component_type,
            s.discipline,
            s.x1,
            s.y1,
            s.x2,
            s.y2
        FROM spatial_entities AS s
        """

        joins = []
        conditions = []
        params = []

        for index, (attribute_name, attribute_value) in enumerate(
            attributes.items()
        ):
            alias = f"a{index}"

            joins.append(
                f"""
                INNER JOIN cleaned_eav AS {alias}
                    ON s.uid = {alias}.uid
                    AND {alias}.attribute_name = ?
                    AND {alias}.attribute_value = ?
                """
            )

            params.extend(
                [str(attribute_name), str(attribute_value)]
            )

        if discipline is not None:
            conditions.append("s.discipline = ?")
            params.append(str(discipline))

        if component_type is not None:
            conditions.append("s.component_type = ?")
            params.append(str(component_type))

        query = base_query

        if joins:
            query += "\n".join(joins)

        if conditions:
            query += "\nWHERE " + "\nAND ".join(conditions)

        query += "\nORDER BY s.uid"

        with sqlite3.connect(DB_PATH) as conn:
            result = pd.read_sql_query(
                query,
                conn,
                params=params,
            )

        elapsed = time.perf_counter() - start_time

        return result, elapsed

    def query_pandas(
        self,
        discipline=None,
        component_type=None,
        attributes=None,
    ):
        """
        Query the flattened Pandas feature table using
        the same filters as query_sqlite().
        """

        if self.feature_table is None:
            self.load_feature_table()

        start_time = time.perf_counter()

        result = self.feature_table.copy()

        if discipline is not None:
            result = result[
                result["discipline"] == str(discipline)
            ]

        if component_type is not None:
            result = result[
                result["component_type"] == str(component_type)
            ]

        attributes = attributes or {}

        for attribute_name, attribute_value in attributes.items():

            if attribute_name not in result.columns:
                result = result.iloc[0:0]
                break

            result = result[
                result[attribute_name] == str(attribute_value)
            ]

        result = (
            result[
                [
                    "uid",
                    "component_type",
                    "discipline",
                    "x1",
                    "y1",
                    "x2",
                    "y2",
                ]
            ]
            .sort_values("uid")
            .reset_index(drop=True)
        )

        elapsed = time.perf_counter() - start_time

        return result, elapsed

    @staticmethod
    def compare_results(sql_result, pandas_result):
        """
        Compare result sets by UID.

        Returns True only if both engines produce
        exactly the same component IDs.
        """

        sql_uids = sorted(sql_result["uid"].astype(str).tolist())

        pandas_uids = sorted(
            pandas_result["uid"].astype(str).tolist()
        )

        return sql_uids == pandas_uids


def print_query_result(
    title,
    discipline,
    component_type,
    attributes,
    result,
    elapsed,
):
    print("-" * 60)
    print(title)
    print("-" * 60)
    print()

    print("Filters:")

    if discipline is not None:
        print(f"  Discipline: {discipline}")

    if component_type is not None:
        print(f"  Component type: {component_type}")

    for attribute_name, attribute_value in attributes.items():
        print(f"  {attribute_name}: {attribute_value}")

    print()
    print(f"Matching components: {len(result):,}")
    print(f"Execution time: {elapsed * 1000:.4f} ms")

    if not result.empty:
        print()
        print("Sample results:")
        print(
            result[
                ["uid", "component_type", "discipline"]
            ]
            .head(5)
            .to_string(index=False)
        )

    print()


def run_test(
    engine,
    test_name,
    discipline=None,
    component_type=None,
    attributes=None,
):
    attributes = attributes or {}

    print("=" * 60)
    print(test_name)
    print("=" * 60)
    print()

    sql_result, sql_time = engine.query_sqlite(
        discipline=discipline,
        component_type=component_type,
        attributes=attributes,
    )

    pandas_result, pandas_time = engine.query_pandas(
        discipline=discipline,
        component_type=component_type,
        attributes=attributes,
    )

    print_query_result(
        "Direct SQLite EAV Query",
        discipline,
        component_type,
        attributes,
        sql_result,
        sql_time,
    )

    print_query_result(
        "Flattened Pandas Query",
        discipline,
        component_type,
        attributes,
        pandas_result,
        pandas_time,
    )

    print("-" * 60)
    print("Result Consistency Check")
    print("-" * 60)

    is_consistent = engine.compare_results(
        sql_result,
        pandas_result,
    )

    if is_consistent:
        print("PASS: SQLite and Pandas results match.")
        print(f"Matching result count: {len(sql_result):,}")
    else:
        print("FAIL: Query result mismatch detected.")
        print(f"SQLite results: {len(sql_result):,}")
        print(f"Pandas results: {len(pandas_result):,}")

        sql_uids = set(sql_result["uid"].astype(str))
        pandas_uids = set(
            pandas_result["uid"].astype(str)
        )

        only_sql = sorted(sql_uids - pandas_uids)
        only_pandas = sorted(pandas_uids - sql_uids)

        if only_sql:
            print(
                "Only in SQLite:",
                ", ".join(only_sql[:10]),
            )

        if only_pandas:
            print(
                "Only in Pandas:",
                ", ".join(only_pandas[:10]),
            )

    print()

    return is_consistent


def main():
    print()
    print("=" * 60)
    print("Engineering EAV Query Engine")
    print("=" * 60)
    print()

    engine = EngineeringQueryEngine()
    engine.load_feature_table()

    tests = [
        {
            "name": "Test 1: Discipline + Material + Status",
            "discipline": "Piping",
            "component_type": None,
            "attributes": {
                "Material": "Carbon_Steel",
                "Status": "Installed",
            },
        },
        {
            "name": "Test 2: Component Type + Status",
            "discipline": None,
            "component_type": "Valve",
            "attributes": {
                "Status": "Installed",
            },
        },
        {
            "name": "Test 3: Electrical Components",
            "discipline": "Electrical",
            "component_type": None,
            "attributes": {
                "Status": "Installed",
            },
        },
        {
            "name": "Test 4: Equipment + Vendor",
            "discipline": "Equipment",
            "component_type": None,
            "attributes": {
                "Vendor": "Vendor_Alpha",
            },
        },
    ]

    passed_tests = 0

    for test in tests:
        passed = run_test(
            engine,
            test_name=test["name"],
            discipline=test["discipline"],
            component_type=test["component_type"],
            attributes=test["attributes"],
        )

        if passed:
            passed_tests += 1

    print("=" * 60)
    print("Final Query Engine Summary")
    print("=" * 60)
    print()
    print(f"Tests passed: {passed_tests}/{len(tests)}")

    if passed_tests == len(tests):
        print("STATUS: ALL QUERY CONSISTENCY TESTS PASSED")
    else:
        print("STATUS: ONE OR MORE CONSISTENCY TESTS FAILED")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
