from __future__ import annotations

from typing import Any

from backend.app.models.engineering_component import (
    EngineeringComponent,
)
from backend.app.repositories.canonical_repository import (
    CanonicalRepository,
)


class ComponentQueryService:
    """
    Application-facing query service.

    This service provides filtering, component lookup,
    viewer data, and connection data for the web application.

    It operates on the canonical engineering model rather
    than directly on the SQLite/EAV database.
    """

    def __init__(
        self,
        repository: CanonicalRepository,
    ) -> None:

        self.repository = repository

    def get_all_components(
        self,
    ) -> list[EngineeringComponent]:

        return self.repository.get_all_components()

    def get_component(
        self,
        component_id: str,
    ) -> EngineeringComponent | None:

        return self.repository.get_component_by_id(
            component_id
        )
    def query_components(
        self,
        component_type: str | None = None,
        discipline: str | None = None,
        zone: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> list[EngineeringComponent]:
        """
        Filter components using semantic fields and
        arbitrary engineering attributes.

        Matching is case-insensitive for strings.
        """

        components = self.repository.get_all_components()

        results = []

        for component in components:

            if (
                component_type is not None
                and component.component_type.lower()
                != component_type.lower()
            ):
                continue

            if (
                discipline is not None
                and component.discipline.lower()
                != discipline.lower()
            ):
                continue

            if (
                zone is not None
                and component.zone.lower()
                != zone.lower()
            ):
                continue

            if attributes is not None:

                attribute_match = True

                # Create a lowercase lookup of component attributes
                component_attributes = {
                    str(name).lower(): value
                    for name, value
                    in component.attributes.items()
                }

                for name, value in attributes.items():

                    component_value = (
                        component_attributes.get(
                            str(name).lower()
                        )
                    )

                    if component_value is None:
                        attribute_match = False
                        break

                    # Case-insensitive comparison for strings
                    if isinstance(component_value, str):

                        if (
                            component_value.lower()
                            != str(value).lower()
                        ):
                            attribute_match = False
                            break

                    elif component_value != value:
                        attribute_match = False
                        break

                if not attribute_match:
                    continue

            results.append(component)

        return results

    def get_matching_component_ids(
        self,
        component_type: str | None = None,
        discipline: str | None = None,
        zone: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> list[str]:
        """
        Return only component IDs.

        This is particularly useful for frontend
        highlighting.
        """

        components = self.query_components(
            component_type=component_type,
            discipline=discipline,
            zone=zone,
            attributes=attributes,
        )

        return [
            component.component_id
            for component in components
        ]

    def get_viewer_components(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return lightweight component data for the
        2D engineering model viewer.
        """

        components = self.repository.get_all_components()

        viewer_components = []

        for component in components:

            viewer_components.append(
                {
                    "component_id": (
                        component.component_id
                    ),

                    "component_type": (
                        component.component_type
                    ),

                    "discipline": (
                        component.discipline
                    ),

                    "zone": component.zone,

                    "geometry": (
                        component.geometry.model_dump()
                    ),
                }
            )

        return viewer_components

    def get_component_connections(
        self,
        component_id: str,
    ) -> list[dict[str, str]]:
        """
        Return all connections associated with a component.
        """

        component = self.get_component(
            component_id
        )

        if component is None:
            return []

        return [
            connection.model_dump()
            for connection in component.connections
        ]

    def get_model_metadata(
        self,
    ) -> dict[str, Any]:
        """
        Return metadata required by the viewer and API.
        """

        return {
            "component_count": (
                self.repository.get_component_count()
            ),

            "bounds": (
                self.repository.get_model_bounds()
            ),
        }