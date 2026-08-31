from __future__ import annotations

import json
from pathlib import Path

from backend.app.models.engineering_component import (
    EngineeringComponent,
)


class CanonicalJSONLWriter:
    """
    Writes canonical EngineeringComponent objects
    as one JSON object per line.
    """

    def __init__(
        self,
        output_path: str | Path,
    ):
        self.output_path = Path(
            output_path
        )

        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def write(
        self,
        components: list[EngineeringComponent],
    ) -> int:

        with self.output_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            for component in components:

                file.write(
                    json.dumps(
                        component.model_dump(
                            mode="json"
                        ),
                        ensure_ascii=False,
                    )
                )

                file.write("\n")

        return len(components)
