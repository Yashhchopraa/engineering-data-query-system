$ProjectRoot = "D:\engineering-data-query-system"
$TargetFile = Join-Path $ProjectRoot "scripts\generate_data.py"

$Content = @'
import argparse
import random
import sqlite3
import time
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = PROJECT_ROOT / "data" / "generated" / "engineering_system.db"


DISCIPLINES = {
    "Piping": {
        "types": ["Pipe_Segment", "Valve", "Flange", "Reducer"],
        "geometry": {
            "Pipe_Segment": "line",
            "Valve": "valve",
            "Flange": "circle",
            "Reducer": "reducer",
        },
        "attrs": {
            "Material": [
                "Carbon_Steel",
                "Stainless_Steel",
                "PVC",
                "Alloy_Steel",
            ],
            "Diameter_mm": ["50", "100", "150", "200", "250", "300"],
            "PressureRating_PSI": ["150", "300", "600"],
            "Insulation": ["Yes", "No"],
            "FluidType": ["Water", "Steam", "Gas", "Oil"],
            "Status": ["Designed", "Procured", "Installed", "Tested"],
            "Vendor": [
                "Vendor_Alpha",
                "Vendor_Beta",
                "Vendor_Gamma",
            ],
        },
    },
    "Equipment": {
        "types": [
            "Pump",
            "Heat_Exchanger",
            "Storage_Tank",
            "Compressor",
        ],
        "geometry": {
            "Pump": "pump",
            "Heat_Exchanger": "equipment",
            "Storage_Tank": "tank",
            "Compressor": "equipment",
        },
        "attrs": {
            "EquipmentType": [
                "Centrifugal",
                "Reciprocating",
                "Shell_and_Tube",
            ],
            "Manufacturer": [
                "GE",
                "Siemens",
                "Sulzer",
                "Flowserve",
            ],
            "Capacity_m3h": ["50", "100", "250", "500"],
            "Voltage_V": ["415", "3300", "6600"],
            "Status": [
                "Ordered",
                "Delivered",
                "Installed",
                "Commissioned",
            ],
            "Vendor": [
                "Vendor_Delta",
                "Vendor_Epsilon",
            ],
        },
    },
    "Structural": {
        "types": [
            "I_Beam",
            "Column",
            "Bracing",
            "Platform",
        ],
        "geometry": {
            "I_Beam": "beam",
            "Column": "column",
            "Bracing": "line",
            "Platform": "rectangle",
        },
        "attrs": {
            "Material_Grade": ["A36", "A572_G50", "S355"],
            "SectionType": [
                "UB_203x133",
                "UC_254x254",
                "PFC_200",
            ],
            "Length_m": ["3.0", "6.0", "9.0", "12.0"],
            "Coating": [
                "Galvanized",
                "Painted_Epoxy",
                "None",
            ],
            "Status": [
                "Fabricated",
                "Erected",
                "Inspected",
            ],
        },
    },
    "Electrical": {
        "types": [
            "Cable_Tray",
            "Transformer",
            "Switchgear",
            "Junction_Box",
        ],
        "geometry": {
            "Cable_Tray": "line",
            "Transformer": "equipment",
            "Switchgear": "equipment",
            "Junction_Box": "rectangle",
        },
        "attrs": {
            "VoltageLevel": [
                "LV_415V",
                "MV_11kV",
                "HV_33kV",
            ],
            "IP_Rating": [
                "IP55",
                "IP65",
                "IP67",
            ],
            "Status": [
                "Laid",
                "Connected",
                "Energized",
            ],
            "Vendor": [
                "Vendor_Zeta",
                "Vendor_Theta",
            ],
        },
    },
    "HVAC": {
        "types": [
            "Duct",
            "Damper",
            "Air_Handler",
            "Diffuser",
        ],
        "geometry": {
            "Duct": "line",
            "Damper": "damper",
            "Air_Handler": "equipment",
            "Diffuser": "circle",
        },
        "attrs": {
            "DuctSize_mm": [
                "200x200",
                "400x300",
                "600x400",
                "800x600",
            ],
            "Airflow_m3h": [
                "500",
                "1200",
                "2500",
                "5000",
            ],
            "PressureClass": [
                "Low",
                "Medium",
                "High",
            ],
            "Material": [
                "Galvanized_Steel",
                "Aluminum",
            ],
            "Insulation": [
                "Acoustic",
                "Thermal",
                "None",
            ],
            "Status": [
                "Fabricated",
                "Installed",
                "Balanced",
                "Commissioned",
            ],
            "Vendor": [
                "Vendor_HVAC_1",
                "Vendor_HVAC_2",
            ],
        },
    },
}


def create_schema(conn):
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS component_connections")
    cursor.execute("DROP TABLE IF EXISTS eav_attributes")
    cursor.execute("DROP TABLE IF EXISTS spatial_entities")

    cursor.execute(
        """
        CREATE TABLE spatial_entities (
            uid TEXT PRIMARY KEY,
            component_type TEXT NOT NULL,
            discipline TEXT NOT NULL,

            geometry_type TEXT NOT NULL,

            x REAL NOT NULL,
            y REAL NOT NULL,
            width REAL NOT NULL,
            height REAL NOT NULL,
            rotation REAL NOT NULL,

            x1 REAL NOT NULL,
            y1 REAL NOT NULL,
            x2 REAL NOT NULL,
            y2 REAL NOT NULL,

            zone TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE eav_attributes (
            uid TEXT NOT NULL,
            attribute_name TEXT NOT NULL,
            attribute_value TEXT NOT NULL,

            FOREIGN KEY (uid)
                REFERENCES spatial_entities(uid)
                ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE component_connections (
            source_uid TEXT NOT NULL,
            target_uid TEXT NOT NULL,
            connection_type TEXT NOT NULL,

            PRIMARY KEY (
                source_uid,
                target_uid,
                connection_type
            ),

            FOREIGN KEY (source_uid)
                REFERENCES spatial_entities(uid)
                ON DELETE CASCADE,

            FOREIGN KEY (target_uid)
                REFERENCES spatial_entities(uid)
                ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        "CREATE INDEX idx_eav_uid "
        "ON eav_attributes(uid)"
    )

    cursor.execute(
        "CREATE INDEX idx_eav_attribute "
        "ON eav_attributes(attribute_name)"
    )

    cursor.execute(
        "CREATE INDEX idx_eav_value "
        "ON eav_attributes(attribute_value)"
    )

    cursor.execute(
        "CREATE INDEX idx_spatial_discipline "
        "ON spatial_entities(discipline)"
    )

    cursor.execute(
        "CREATE INDEX idx_spatial_type "
        "ON spatial_entities(component_type)"
    )

    cursor.execute(
        "CREATE INDEX idx_spatial_zone "
        "ON spatial_entities(zone)"
    )

    cursor.execute(
        "CREATE INDEX idx_connection_source "
        "ON component_connections(source_uid)"
    )

    cursor.execute(
        "CREATE INDEX idx_connection_target "
        "ON component_connections(target_uid)"
    )


def generate_geometry(rng, geometry_type):
    zone_size = 250

    zone_x = rng.choice([0, 1, 2, 3])
    zone_y = rng.choice([0, 1, 2])

    base_x = zone_x * zone_size + 25
    base_y = zone_y * zone_size + 25

    x = base_x + rng.uniform(0, 180)
    y = base_y + rng.uniform(0, 180)

    rotation = rng.choice([0, 90, 180, 270])

    if geometry_type == "line":
        width = rng.uniform(35, 80)
        height = rng.uniform(8, 15)

    elif geometry_type == "circle":
        width = rng.uniform(18, 30)
        height = width

    elif geometry_type == "tank":
        width = rng.uniform(35, 55)
        height = rng.uniform(45, 70)

    elif geometry_type == "column":
        width = rng.uniform(10, 20)
        height = rng.uniform(35, 65)

    elif geometry_type == "valve":
        width = rng.uniform(18, 28)
        height = rng.uniform(18, 28)

    elif geometry_type == "damper":
        width = rng.uniform(20, 30)
        height = rng.uniform(15, 25)

    elif geometry_type == "beam":
        width = rng.uniform(50, 100)
        height = rng.uniform(8, 15)

    elif geometry_type == "reducer":
        width = rng.uniform(25, 45)
        height = rng.uniform(12, 22)

    else:
        width = rng.uniform(25, 50)
        height = rng.uniform(25, 50)

    x2 = min(x + width, 995)
    y2 = min(y + height, 745)

    zone = f"ZONE-{zone_y + 1}-{zone_x + 1}"

    return (
        round(x, 2),
        round(y, 2),
        round(width, 2),
        round(height, 2),
        float(rotation),
        round(x, 2),
        round(y, 2),
        round(x2, 2),
        round(y2, 2),
        zone,
    )


def choose_discipline(rng):
    return rng.choice(list(DISCIPLINES.keys()))


def generate_components(num_components, seed):
    rng = random.Random(seed)

    entities = []
    eav_rows = []
    discipline_counter = Counter()
    type_counter = Counter()

    for index in range(1, num_components + 1):
        uid = f"CMP-{100000 + index}"

        discipline = choose_discipline(rng)
        definition = DISCIPLINES[discipline]

        component_type = rng.choice(definition["types"])
        geometry_type = definition["geometry"][component_type]

        geometry = generate_geometry(
            rng,
            geometry_type,
        )

        (
            x,
            y,
            width,
            height,
            rotation,
            x1,
            y1,
            x2,
            y2,
            zone,
        ) = geometry

        entities.append(
            (
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
                zone,
            )
        )

        discipline_counter[discipline] += 1
        type_counter[component_type] += 1

        for attribute_name, values in definition["attrs"].items():
            if rng.random() > 0.10:
                value = rng.choice(values)

                eav_rows.append(
                    (
                        uid,
                        attribute_name,
                        value,
                    )
                )

    return (
        entities,
        eav_rows,
        discipline_counter,
        type_counter,
    )


def generate_connections(entities, seed):
    """
    Creates a deterministic lightweight topology.

    Connections are generated primarily between components
    occupying the same spatial zone. This is intentionally
    simplified and is not intended to reproduce real CAD
    connectivity.
    """

    rng = random.Random(seed + 1000)

    by_zone = {}

    for entity in entities:
        uid = entity[0]
        zone = entity[13]

        by_zone.setdefault(zone, []).append(uid)

    connections = []

    for zone_uids in by_zone.values():
        shuffled = list(zone_uids)
        rng.shuffle(shuffled)

        for index in range(len(shuffled) - 1):
            source = shuffled[index]
            target = shuffled[index + 1]

            if source == target:
                continue

            connection_type = rng.choice(
                [
                    "physical",
                    "process",
                    "adjacent",
                ]
            )

            connections.append(
                (
                    source,
                    target,
                    connection_type,
                )
            )

    return connections


def inject_anomalies(
    rng,
    eav_rows,
    num_components,
):
    if num_components < 100:
        return {
            "duplicate_cases": 0,
            "invalid_numeric": 0,
            "schema_pollution": 0,
        }

    anomaly_count = max(
        1,
        int(num_components * 0.01),
    )

    duplicate_count = 0
    invalid_count = 0
    pollution_count = 0

    # Duplicate Status values.
    for _ in range(anomaly_count):
        target_index = rng.randint(
            1,
            num_components,
        )

        uid = f"CMP-{100000 + target_index}"

        eav_rows.append(
            (
                uid,
                "Status",
                "Installed",
            )
        )

        eav_rows.append(
            (
                uid,
                "Status",
                "Commissioned",
            )
        )

        duplicate_count += 1

    # Invalid pressure values are attached to
    # randomly selected components.
    for _ in range(anomaly_count):
        target_index = rng.randint(
            1,
            num_components,
        )

        uid = f"CMP-{100000 + target_index}"

        eav_rows.append(
            (
                uid,
                "PressureRating_PSI",
                "-9999",
            )
        )

        invalid_count += 1

    # Unexpected attribute.
    for index in range(1, anomaly_count + 1):
        target_index = rng.randint(
            1,
            num_components,
        )

        uid = f"CMP-{100000 + target_index}"

        eav_rows.append(
            (
                uid,
                "ContaminatedPath",
                f"C:/Synthetic/Temp/Config_{index}.dat",
            )
        )

        pollution_count += 1

    return {
        "duplicate_cases": duplicate_count,
        "invalid_numeric": invalid_count,
        "schema_pollution": pollution_count,
    }


def build_database(
    db_path,
    num_components,
    seed=42,
    inject_anomaly_data=True,
):
    start_time = time.perf_counter()

    rng = random.Random(seed)

    db_path = Path(db_path)
    db_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    create_schema(conn)

    (
        entities,
        eav_rows,
        discipline_counter,
        type_counter,
    ) = generate_components(
        num_components,
        seed,
    )

    if inject_anomaly_data:
        anomaly_summary = inject_anomalies(
            rng,
            eav_rows,
            num_components,
        )
    else:
        anomaly_summary = {
            "duplicate_cases": 0,
            "invalid_numeric": 0,
            "schema_pollution": 0,
        }

    connections = generate_connections(
        entities,
        seed,
    )

    cursor = conn.cursor()

    cursor.executemany(
        """
        INSERT INTO spatial_entities (
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
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?
        )
        """,
        entities,
    )

    cursor.executemany(
        """
        INSERT INTO eav_attributes (
            uid,
            attribute_name,
            attribute_value
        )
        VALUES (?, ?, ?)
        """,
        eav_rows,
    )

    cursor.executemany(
        """
        INSERT INTO component_connections (
            source_uid,
            target_uid,
            connection_type
        )
        VALUES (?, ?, ?)
        """,
        connections,
    )

    conn.commit()

    spatial_count = cursor.execute(
        "SELECT COUNT(*) FROM spatial_entities"
    ).fetchone()[0]

    eav_count = cursor.execute(
        "SELECT COUNT(*) FROM eav_attributes"
    ).fetchone()[0]

    connection_count = cursor.execute(
        "SELECT COUNT(*) FROM component_connections"
    ).fetchone()[0]

    unique_attributes = cursor.execute(
        """
        SELECT COUNT(DISTINCT attribute_name)
        FROM eav_attributes
        """
    ).fetchone()[0]

    conn.close()

    elapsed = time.perf_counter() - start_time

    print()
    print("=" * 60)
    print("Synthetic Engineering Data Generator v4")
    print("=" * 60)
    print()
    print(f"Components requested: {num_components:,}")
    print(f"Random seed:          {seed}")
    print("Missing attribute rate: 10.0%")
    print()
    print("Generating semantic engineering model...")
    print()
    print(f"Generated entities:       {spatial_count:,}")
    print(f"Generated EAV rows:       {eav_count:,}")
    print(f"Generated connections:    {connection_count:,}")
    print()
    print("Discipline Distribution")
    print("-" * 40)

    for discipline, count in sorted(
        discipline_counter.items()
    ):
        print(
            f"{discipline:<20} {count:,}"
        )

    print()
    print("Model Representation")
    print("-" * 40)
    print("Geometry:                 Semantic 2D geometry")
    print("Spatial bounds:           x1/y1/x2/y2")
    print("Zones:                    12 synthetic zones")
    print("Connectivity:             Component graph")
    print(f"Unique attributes:        {unique_attributes:,}")

    print()
    print("Controlled Anomalies")
    print("-" * 40)
    print(
        f"Duplicate cases:          "
        f"{anomaly_summary['duplicate_cases']:,}"
    )
    print(
        f"Invalid numeric values:   "
        f"{anomaly_summary['invalid_numeric']:,}"
    )
    print(
        f"Schema pollution:         "
        f"{anomaly_summary['schema_pollution']:,}"
    )

    print()
    print(f"Database created: {db_path}")
    print(f"Total generation time: {elapsed:.3f} seconds")
    print("=" * 60)
    print()


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Synthetic Engineering Model Generator v4"
        )
    )

    parser.add_argument(
        "--components",
        type=int,
        default=1000,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
    )

    args = parser.parse_args()

    build_database(
        db_path=args.db,
        num_components=args.components,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
'@

Set-Content -Path $TargetFile -Value $Content -Encoding UTF8

Write-Host ""
Write-Host "Successfully wrote:"
Write-Host $TargetFile