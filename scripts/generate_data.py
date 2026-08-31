import argparse
import random
import sqlite3
import time
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_DB = (
    PROJECT_ROOT
    / "data"
    / "generated"
    / "engineering_system.db"
)


# ============================================================
# DISCIPLINE DEFINITIONS
# ============================================================

DISCIPLINES = {
    "Piping": {
        "types": [
            "Pipe_Segment",
            "Valve",
            "Flange",
            "Reducer",
        ],

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

            "Diameter_mm": [
                "50",
                "100",
                "150",
                "200",
                "250",
                "300",
            ],

            "PressureRating_PSI": [
                "150",
                "300",
                "600",
            ],

            "Insulation": [
                "Yes",
                "No",
            ],

            "FluidType": [
                "Water",
                "Steam",
                "Gas",
                "Oil",
            ],

            "Status": [
                "Designed",
                "Procured",
                "Installed",
                "Tested",
            ],

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

            "Capacity_m3h": [
                "50",
                "100",
                "250",
                "500",
            ],

            "Voltage_V": [
                "415",
                "3300",
                "6600",
            ],

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
            "Material_Grade": [
                "A36",
                "A572_G50",
                "S355",
            ],

            "SectionType": [
                "UB_203x133",
                "UC_254x254",
                "PFC_200",
            ],

            "Length_m": [
                "3.0",
                "6.0",
                "9.0",
                "12.0",
            ],

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


# ============================================================
# PLANT LAYOUT
# ============================================================

ZONE_WIDTH = 520
ZONE_HEIGHT = 380

ZONE_COLUMNS = 3
ZONE_ROWS = 4

PLANT_WIDTH = ZONE_COLUMNS * ZONE_WIDTH
PLANT_HEIGHT = ZONE_ROWS * ZONE_HEIGHT


# ============================================================
# DATABASE SCHEMA
# ============================================================

def create_schema(conn):

    cursor = conn.cursor()

    cursor.execute(
        "DROP TABLE IF EXISTS component_connections"
    )

    cursor.execute(
        "DROP TABLE IF EXISTS eav_attributes"
    )

    cursor.execute(
        "DROP TABLE IF EXISTS spatial_entities"
    )

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


# ============================================================
# COMPONENT SIZE
# ============================================================

def get_geometry_size(
    rng,
    discipline,
    geometry_type,
):

    if discipline == "Piping":

        if geometry_type == "line":
            return (
                rng.uniform(90, 180),
                rng.uniform(6, 10),
                rng.choice([0, 0, 0, 90]),
            )

        if geometry_type == "valve":
            size = rng.uniform(18, 28)
            return size, size, 0

        if geometry_type == "circle":
            size = rng.uniform(18, 26)
            return size, size, 0

        if geometry_type == "reducer":
            return (
                rng.uniform(25, 45),
                rng.uniform(12, 18),
                0,
            )

    if discipline == "Equipment":

        if geometry_type == "tank":
            return (
                rng.uniform(55, 80),
                rng.uniform(85, 125),
                0,
            )

        if geometry_type == "pump":
            size = rng.uniform(38, 55)
            return size, size, 0

        return (
            rng.uniform(55, 85),
            rng.uniform(45, 75),
            0,
        )

    if discipline == "Structural":

        if geometry_type == "beam":
            return (
                rng.uniform(110, 180),
                rng.uniform(8, 14),
                0,
            )

        if geometry_type == "column":
            return (
                rng.uniform(12, 20),
                rng.uniform(65, 100),
                0,
            )

        if geometry_type == "line":
            return (
                rng.uniform(80, 140),
                rng.uniform(5, 9),
                rng.choice([0, 90]),
            )

        return (
            rng.uniform(60, 100),
            rng.uniform(30, 50),
            0,
        )

    if discipline == "Electrical":

        if geometry_type == "line":
            return (
                rng.uniform(100, 170),
                rng.uniform(7, 11),
                0,
            )

        return (
            rng.uniform(35, 65),
            rng.uniform(30, 60),
            0,
        )

    if discipline == "HVAC":

        if geometry_type == "line":
            return (
                rng.uniform(100, 180),
                rng.uniform(9, 15),
                rng.choice([0, 90]),
            )

        if geometry_type == "circle":
            size = rng.uniform(20, 30)
            return size, size, 0

        if geometry_type == "damper":
            return (
                rng.uniform(20, 32),
                rng.uniform(15, 25),
                0,
            )

        return (
            rng.uniform(45, 75),
            rng.uniform(40, 65),
            0,
        )

    return (
        rng.uniform(30, 60),
        rng.uniform(30, 60),
        0,
    )


# ============================================================
# SPATIAL PLACEMENT
# ============================================================

def generate_geometry(
    rng,
    geometry_type,
    discipline,
    component_index,
):
    """
    Generate a structured plant-layout style 2D model.

    The plant is divided into 12 zones.
    Each zone contains dedicated spatial areas for:
        - Structural
        - Equipment
        - Piping
        - Electrical
        - HVAC

    Components are distributed across the zone rather than
    repeatedly occupying the same coordinates.
    """

    # ========================================================
    # ZONE
    # ========================================================

    zone_index = (
        component_index - 1
    ) % 12

    zone_column = zone_index % 3
    zone_row = zone_index // 3

    zone = (
        f"ZONE-{zone_row + 1}-"
        f"{zone_column + 1}"
    )

    zone_origin_x = (
        zone_column * ZONE_WIDTH
    )

    zone_origin_y = (
        zone_row * ZONE_HEIGHT
    )

    # ========================================================
    # GEOMETRY SIZE
    # ========================================================

    width, height, rotation = (
        get_geometry_size(
            rng,
            discipline,
            geometry_type,
        )
    )

    # ========================================================
    # LOCAL COMPONENT INDEX
    #
    # Each zone receives approximately 83 components.
    # This gives us a stable local index within each zone.
    # ========================================================

    local_index = (
        component_index - 1
    ) // 12

    # ========================================================
    # DISCIPLINE OFFSET
    #
    # Separate disciplines into different physical areas.
    # ========================================================

    discipline_offsets = {

        "Structural": {
            "x": 25,
            "y": 25,
            "width": 470,
            "height": 85,
        },

        "Equipment": {
            "x": 25,
            "y": 120,
            "width": 470,
            "height": 95,
        },

        "Piping": {
            "x": 25,
            "y": 215,
            "width": 470,
            "height": 55,
        },

        "Electrical": {
            "x": 25,
            "y": 275,
            "width": 470,
            "height": 45,
        },

        "HVAC": {
            "x": 25,
            "y": 325,
            "width": 470,
            "height": 40,
        },
    }

    area = discipline_offsets[
        discipline
    ]

    # ========================================================
    # LOCAL POSITION
    # ========================================================

    # Spread components across a 7 x 12 logical grid.
    #
    # This prevents the old "15 positions per zone"
    # problem.

    slot = (
        local_index
        % 84
    )

    column = slot % 7
    row = slot // 7

    cell_width = (
        area["width"] / 7
    )

    cell_height = (
        area["height"] / 12
    )

    x = (
        zone_origin_x
        + area["x"]
        + column * cell_width
        + cell_width / 2
        - width / 2
    )

    y = (
        zone_origin_y
        + area["y"]
        + row * cell_height
        + cell_height / 2
        - height / 2
    )

    # ========================================================
    # DISCIPLINE-SPECIFIC ENGINEERING LAYOUT
    # ========================================================

    # --------------------------------------------------------
    # STRUCTURAL
    # --------------------------------------------------------

    if discipline == "Structural":

        if geometry_type == "column":

            # Columns form vertical structural members.
            column_slot = (
                local_index % 6
            )

            x = (
                zone_origin_x
                + 45
                + column_slot * 80
            )

            y = (
                zone_origin_y
                + 25
            )

            height = min(
                height,
                75,
            )

        elif geometry_type == "beam":

            # Beams span across the structural area.
            x = (
                zone_origin_x
                + 30
            )

            y = (
                zone_origin_y
                + 55
                + (
                    local_index % 3
                ) * 25
            )

            width = min(
                width,
                430,
            )

        elif geometry_type == "line":

            rotation = (
                90
                if local_index % 2
                else 0
            )

    # --------------------------------------------------------
    # EQUIPMENT
    # --------------------------------------------------------

    elif discipline == "Equipment":

        equipment_slot = (
            local_index % 20
        )

        equipment_column = (
            equipment_slot % 5
        )

        equipment_row = (
            equipment_slot // 5
        )

        x = (
            zone_origin_x
            + 40
            + equipment_column * 88
            - width / 2
        )

        y = (
            zone_origin_y
            + 125
            + equipment_row * 22
        )

    # --------------------------------------------------------
    # PIPING
    # --------------------------------------------------------

    elif discipline == "Piping":

        if geometry_type == "line":

            # Long horizontal pipe corridors.
            pipe_lane = (
                local_index % 4
            )

            x = (
                zone_origin_x
                + 30
            )

            y = (
                zone_origin_y
                + 220
                + pipe_lane * 13
            )

            width = min(
                width,
                430,
            )

            rotation = 0

        else:

            # Valves, reducers and flanges
            # are distributed along pipe corridors.

            pipe_position = (
                local_index % 18
            )

            x = (
                zone_origin_x
                + 40
                + (pipe_position % 9) * 48
            )

            y = (
                zone_origin_y
                + 218
                + (pipe_position // 9) * 25
            )

            if geometry_type == "valve":

                rotation = (
                    90
                    if pipe_position % 2
                    else 0
                )

    # --------------------------------------------------------
    # ELECTRICAL
    # --------------------------------------------------------

    elif discipline == "Electrical":

        electrical_slot = (
            local_index % 15
        )

        column = (
            electrical_slot % 5
        )

        row = (
            electrical_slot // 5
        )

        x = (
            zone_origin_x
            + 45
            + column * 90
            - width / 2
        )

        y = (
            zone_origin_y
            + 270
            + row * 17
        )

        if geometry_type == "line":

            x = (
                zone_origin_x
                + 30
            )

            y = (
                zone_origin_y
                + 300
            )

            width = min(
                width,
                430,
            )

    # --------------------------------------------------------
    # HVAC
    # --------------------------------------------------------

    elif discipline == "HVAC":

        if geometry_type == "line":

            duct_lane = (
                local_index % 3
            )

            x = (
                zone_origin_x
                + 30
            )

            y = (
                zone_origin_y
                + 325
                + duct_lane * 11
            )

            width = min(
                width,
                430,
            )

            rotation = 0

        else:

            hvac_slot = (
                local_index % 12
            )

            column = (
                hvac_slot % 6
            )

            row = (
                hvac_slot // 6
            )

            x = (
                zone_origin_x
                + 40
                + column * 75
                - width / 2
            )

            y = (
                zone_origin_y
                + 320
                + row * 18
            )

    # ========================================================
    # SMALL RANDOM VARIATION
    # ========================================================

    x += rng.uniform(
        -4,
        4,
    )

    y += rng.uniform(
        -3,
        3,
    )

    # ========================================================
    # BOUNDARIES
    # ========================================================

    x = max(
        zone_origin_x + 8,
        min(
            x,
            zone_origin_x
            + ZONE_WIDTH
            - width
            - 8,
        ),
    )

    y = max(
        zone_origin_y + 8,
        min(
            y,
            zone_origin_y
            + ZONE_HEIGHT
            - height
            - 8,
        ),
    )

    # ========================================================
    # END POINTS
    # ========================================================

    x2 = x + width
    y2 = y + height

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

# ============================================================
# DISCIPLINE SELECTION
# ============================================================

def choose_discipline(rng):

    return rng.choices(
        [
            "Piping",
            "Equipment",
            "Structural",
            "Electrical",
            "HVAC",
        ],

        weights=[
            28,
            20,
            22,
            15,
            15,
        ],

        k=1,
    )[0]


# ============================================================
# COMPONENT GENERATION
# ============================================================

def generate_components(
    num_components,
    seed,
):

    rng = random.Random(seed)

    entities = []

    eav_rows = []

    discipline_counter = Counter()

    type_counter = Counter()

    for index in range(
        1,
        num_components + 1,
    ):

        uid = (
            f"CMP-{100000 + index}"
        )

        discipline = (
            choose_discipline(rng)
        )

        definition = (
            DISCIPLINES[discipline]
        )

        component_type = (
            rng.choice(
                definition["types"]
            )
        )

        geometry_type = (
            definition["geometry"][
                component_type
            ]
        )

        geometry = generate_geometry(
            rng,
            geometry_type,
            discipline,
            index,
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

        discipline_counter[
            discipline
        ] += 1

        type_counter[
            component_type
        ] += 1

        # ----------------------------------------------------
        # EAV
        # ----------------------------------------------------

        for (
            attribute_name,
            values,
        ) in definition["attrs"].items():

            if rng.random() > 0.10:

                value = rng.choice(
                    values
                )

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


# ============================================================
# CONNECTIONS
# ============================================================

def generate_connections(
    entities,
    seed,
):

    rng = random.Random(
        seed + 1000
    )

    by_zone = {}

    for entity in entities:

        uid = entity[0]

        zone = entity[13]

        by_zone.setdefault(
            zone,
            [],
        ).append(entity)

    connections = []

    # --------------------------------------------------------
    # Connect nearby components in the same zone.
    # --------------------------------------------------------

    for zone_entities in (
        by_zone.values()
    ):

        for source in zone_entities:

            source_uid = source[0]

            source_discipline = source[2]

            source_x = source[4]

            source_y = source[5]

            candidates = []

            for target in zone_entities:

                if (
                    target[0]
                    == source_uid
                ):
                    continue

                distance = (
                    abs(
                        target[4]
                        - source_x
                    )
                    +
                    abs(
                        target[5]
                        - source_y
                    )
                )

                # Only consider nearby components.
                if distance < 180:

                    candidates.append(
                        (
                            distance,
                            target,
                        )
                    )

            candidates.sort(
                key=lambda item:
                item[0]
            )

            # Connect to the closest 1-2
            # relevant components.

            for (
                _,
                target,
            ) in candidates[:2]:

                target_uid = target[0]

                target_discipline = (
                    target[2]
                )

                if (
                    source_discipline
                    == "Piping"
                    or target_discipline
                    == "Piping"
                ):

                    connection_type = (
                        "process"
                    )

                elif (
                    source_discipline
                    == "Structural"
                    or target_discipline
                    == "Structural"
                ):

                    connection_type = (
                        "support"
                    )

                else:

                    connection_type = (
                        rng.choice(
                            [
                                "physical",
                                "adjacent",
                            ]
                        )
                    )

                connections.append(
                    (
                        source_uid,
                        target_uid,
                        connection_type,
                    )
                )

    # Remove duplicates.
    connections = list(
        dict.fromkeys(
            connections
        )
    )

    return connections


# ============================================================
# ANOMALIES
# ============================================================

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
        int(
            num_components
            * 0.01
        ),
    )

    duplicate_count = 0
    invalid_count = 0
    pollution_count = 0

    # --------------------------------------------------------
    # Duplicate values
    # --------------------------------------------------------

    for _ in range(
        anomaly_count
    ):

        target_index = (
            rng.randint(
                1,
                num_components,
            )
        )

        uid = (
            f"CMP-{100000 + target_index}"
        )

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

    # --------------------------------------------------------
    # Invalid numeric data
    # --------------------------------------------------------

    for _ in range(
        anomaly_count
    ):

        target_index = (
            rng.randint(
                1,
                num_components,
            )
        )

        uid = (
            f"CMP-{100000 + target_index}"
        )

        eav_rows.append(
            (
                uid,
                "PressureRating_PSI",
                "-9999",
            )
        )

        invalid_count += 1

    # --------------------------------------------------------
    # Schema pollution
    # --------------------------------------------------------

    for index in range(
        1,
        anomaly_count + 1,
    ):

        target_index = (
            rng.randint(
                1,
                num_components,
            )
        )

        uid = (
            f"CMP-{100000 + target_index}"
        )

        eav_rows.append(
            (
                uid,
                "ContaminatedPath",
                (
                    f"C:/Synthetic/Temp/"
                    f"Config_{index}.dat"
                ),
            )
        )

        pollution_count += 1

    return {
        "duplicate_cases":
            duplicate_count,

        "invalid_numeric":
            invalid_count,

        "schema_pollution":
            pollution_count,
    }


# ============================================================
# DATABASE BUILD
# ============================================================

def build_database(
    db_path,
    num_components,
    seed=42,
    inject_anomaly_data=True,
):

    start_time = (
        time.perf_counter()
    )

    rng = random.Random(
        seed
    )

    db_path = Path(
        db_path
    )

    db_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(
        db_path
    )

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    create_schema(
        conn
    )

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

        anomaly_summary = (
            inject_anomalies(
                rng,
                eav_rows,
                num_components,
            )
        )

    else:

        anomaly_summary = {
            "duplicate_cases": 0,
            "invalid_numeric": 0,
            "schema_pollution": 0,
        }

    connections = (
        generate_connections(
            entities,
            seed,
        )
    )

    cursor = conn.cursor()

    # --------------------------------------------------------
    # Spatial entities
    # --------------------------------------------------------

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
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?
        )
        """,
        entities,
    )

    # --------------------------------------------------------
    # EAV
    # --------------------------------------------------------

    cursor.executemany(
        """
        INSERT INTO eav_attributes (

            uid,
            attribute_name,
            attribute_value

        )

        VALUES (
            ?, ?, ?
        )
        """,
        eav_rows,
    )

    # --------------------------------------------------------
    # Connections
    # --------------------------------------------------------

    cursor.executemany(
        """
        INSERT INTO component_connections (

            source_uid,
            target_uid,
            connection_type

        )

        VALUES (
            ?, ?, ?
        )
        """,
        connections,
    )

    conn.commit()

    spatial_count = cursor.execute(
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

    connection_count = cursor.execute(
        """
        SELECT COUNT(*)
        FROM component_connections
        """
    ).fetchone()[0]

    unique_attributes = cursor.execute(
        """
        SELECT COUNT(
            DISTINCT attribute_name
        )
        FROM eav_attributes
        """
    ).fetchone()[0]

    zone_count = cursor.execute(
        """
        SELECT COUNT(
            DISTINCT zone
        )
        FROM spatial_entities
        """
    ).fetchone()[0]

    conn.close()

    elapsed = (
        time.perf_counter()
        - start_time
    )

    # ========================================================
    # REPORT
    # ========================================================

    print()

    print(
        "=" * 60
    )

    print(
        "Synthetic Engineering Data Generator v5"
    )

    print(
        "=" * 60
    )

    print()

    print(
        f"Components requested: "
        f"{num_components:,}"
    )

    print(
        f"Random seed:          "
        f"{seed}"
    )

    print(
        "Missing attribute rate: 10.0%"
    )

    print()

    print(
        "Generating structured plant model..."
    )

    print()

    print(
        f"Generated entities:       "
        f"{spatial_count:,}"
    )

    print(
        f"Generated EAV rows:       "
        f"{eav_count:,}"
    )

    print(
        f"Generated connections:    "
        f"{connection_count:,}"
    )

    print()

    print(
        "Discipline Distribution"
    )

    print(
        "-" * 40
    )

    for (
        discipline,
        count,
    ) in sorted(
        discipline_counter.items()
    ):

        print(
            f"{discipline:<20}"
            f"{count:,}"
        )

    print()

    print(
        "Model Representation"
    )

    print(
        "-" * 40
    )

    print(
        "Geometry:                 "
        "Structured semantic 2D"
    )

    print(
        "Plant layout:             "
        f"{ZONE_COLUMNS} x "
        f"{ZONE_ROWS} zones"
    )

    print(
        "Spatial bounds:           "
        "x1/y1/x2/y2"
    )

    print(
        f"Zones:                    "
        f"{zone_count}"
    )

    print(
        "Connectivity:             "
        "Spatial/discipline graph"
    )

    print(
        f"Unique attributes:        "
        f"{unique_attributes:,}"
    )

    print()

    print(
        "Controlled Anomalies"
    )

    print(
        "-" * 40
    )

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

    print(
        f"Database created: "
        f"{db_path}"
    )

    print(
        f"Total generation time: "
        f"{elapsed:.3f} seconds"
    )

    print(
        "=" * 60
    )

    print()


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Synthetic Engineering "
            "Model Generator v5"
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