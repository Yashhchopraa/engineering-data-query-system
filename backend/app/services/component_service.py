from __future__ import annotations

from collections import defaultdict
from typing import Any

from backend.app.models.engineering_component import (
    ComponentConnection,
    DataQuality,
    EngineeringComponent,
    Geometry,
)
from backend.app.repositories.sqlite_repository import (
    SQLiteEngineeringRepository,
)


class EngineeringComponentService:
    """
    Converts repository records into canonical
    EngineeringComponent objects.
    """

    def __init__(
        self,
        repository: SQLiteEngineeringRepository,
    ):
        self.repository = repository

    def build_components(
        self,
    ) -> list[EngineeringComponent]:

        entities = self.repository.get_entities()

        attributes = self.repository.get_attributes()

        connections = self.repository.get_connections()

        attributes_by_uid = defaultdict(list)

        for row in attributes:
            attributes_by_uid[row["uid"]].append(row)

        connections_by_uid = defaultdict(list)

        for row in connections:
            connections_by_uid[
                row["source_uid"]
            ].append(row)

            connections_by_uid[
                row["target_uid"]
            ].append(row)

        components = []

        for entity in entities:

            uid = entity["uid"]

            raw_attributes = attributes_by_uid.get(
                uid,
                [],
            )

            attribute_map: dict[str, Any] = {}

            duplicate_found = False

            duplicate_names: set[str] = set()

            for row in raw_attributes:

                name = row["attribute_name"]

                if name in attribute_map:
                    duplicate_found = True
                    duplicate_names.add(name)
                    continue

                attribute_map[name] = (
                    row["attribute_value"]
                )

            component_connections = []

            for connection in connections_by_uid.get(
                uid,
                [],
            ):
                component_connections.append(
                    ComponentConnection(
                        source_uid=connection[
                            "source_uid"
                        ],
                        target_uid=connection[
                            "target_uid"
                        ],
                        connection_type=connection[
                            "connection_type"
                        ],
                    )
                )

            flags = []

            if duplicate_found:
                flags.append(
                    "duplicate_attribute_resolved"
                )

            if "ContaminatedPath" in attribute_map:
                flags.append(
                    "unexpected_attribute"
                )

            if (
                "PressureRating_PSI"
                in attribute_map
            ):
                try:
                    pressure = float(
                        attribute_map[
                            "PressureRating_PSI"
                        ]
                    )

                    if pressure < 0:
                        flags.append(
                            "invalid_numeric_value"
                        )

                except ValueError:
                    flags.append(
                        "invalid_numeric_value"
                    )

            component = EngineeringComponent(
                component_id=uid,

                component_type=entity[
                    "component_type"
                ],

                discipline=entity[
                    "discipline"
                ],

                zone=entity["zone"],

                geometry=Geometry(
                    geometry_type=entity[
                        "geometry_type"
                    ],

                    x=entity["x"],
                    y=entity["y"],

                    width=entity[
                        "width"
                    ],

                    height=entity[
                        "height"
                    ],

                    rotation=entity[
                        "rotation"
                    ],

                    x1=entity["x1"],
                    y1=entity["y1"],
                    x2=entity["x2"],
                    y2=entity["y2"],
                ),

                attributes=attribute_map,

                connections=component_connections,

                data_quality=DataQuality(
                    flags=flags,

                    duplicate_attributes_resolved=(
                        duplicate_found
                    ),

                    unknown_attributes=list(
                        duplicate_names
                    ),
                ),
            )

            components.append(component)

        return components

    def get_component(
        self,
        uid: str,
    ) -> EngineeringComponent | None:

        components = self.build_components()

        for component in components:
            if component.component_id == uid:
                return component

        return None
