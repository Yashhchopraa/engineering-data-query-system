from __future__ import annotations

import json
from pathlib import Path

from backend.app.models.engineering_component import EngineeringComponent


PROJECT_ROOT = Path(__file__).resolve().parents[3]

CANONICAL_MODEL_PATH = (
    PROJECT_ROOT
    / "data"
    / "canonical"
    / "engineering_components.jsonl"
)


class CanonicalRepository:
    """
    Repository for accessing the canonical engineering model.

    The repository is responsible only for loading and retrieving
    EngineeringComponent objects from the canonical JSONL dataset.
    """

    def __init__(
        self,
        model_path: Path | None = None,
    ) -> None:

        self.model_path = (
            model_path
            if model_path is not None
            else CANONICAL_MODEL_PATH
        )

        self._components: list[EngineeringComponent] = []
        self._component_index: dict[
            str,
            EngineeringComponent
        ] = {}

        self._load()

    def _load(self) -> None:
        """
        Load canonical components from the JSONL file.
        """

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Canonical model not found: {self.model_path}"
            )

        with self.model_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                data = json.loads(line)

                component = EngineeringComponent(
                    **data
                )

                self._components.append(
                    component
                )

                self._component_index[
                    component.component_id
                ] = component

    def get_all_components(
        self,
    ) -> list[EngineeringComponent]:

        return self._components

    def get_component_by_id(
        self,
        component_id: str,
    ) -> EngineeringComponent | None:

        return self._component_index.get(
            component_id
        )

    def get_components_by_ids(
        self,
        component_ids: list[str],
    ) -> list[EngineeringComponent]:

        return [
            component
            for component_id in component_ids
            if (
                component :=
                self._component_index.get(component_id)
            )
            is not None
        ]

    def get_component_count(self) -> int:

        return len(self._components)

    def get_model_bounds(self) -> dict[str, float]:
        """
        Calculate the overall spatial bounds of the model.
        """

        if not self._components:
            return {
                "min_x": 0.0,
                "min_y": 0.0,
                "max_x": 0.0,
                "max_y": 0.0,
            }

        return {
            "min_x": min(
                component.geometry.x1
                for component in self._components
            ),
            "min_y": min(
                component.geometry.y1
                for component in self._components
            ),
            "max_x": max(
                component.geometry.x2
                for component in self._components
            ),
            "max_y": max(
                component.geometry.y2
                for component in self._components
            ),
        }