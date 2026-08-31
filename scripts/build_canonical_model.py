from pathlib import Path

from backend.app.repositories.sqlite_repository import (
    SQLiteEngineeringRepository,
)

from backend.app.services.component_service import (
    EngineeringComponentService,
)

from backend.app.storage.canonical_writer import (
    CanonicalJSONLWriter,
)


PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent

DB_PATH = (
    PROJECT_ROOT
    / "data"
    / "generated"
    / "engineering_system.db"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "canonical"
    / "engineering_components.jsonl"
)


def main():

    print()
    print("=" * 60)
    print("Canonical Engineering Model Builder")
    print("=" * 60)
    print()

    print(
        f"Source database: {DB_PATH}"
    )

    repository = SQLiteEngineeringRepository(
        DB_PATH
    )

    print(
        f"Entities available: "
        f"{repository.count_entities():,}"
    )

    print(
        f"Connections available: "
        f"{repository.count_connections():,}"
    )

    print()
    print(
        "Transforming source records "
        "into canonical components..."
    )

    service = EngineeringComponentService(
        repository
    )

    components = service.build_components()

    print(
        f"Canonical components created: "
        f"{len(components):,}"
    )

    writer = CanonicalJSONLWriter(
        OUTPUT_PATH
    )

    written = writer.write(
        components
    )

    print()
    print("=" * 60)
    print("Canonical Model Summary")
    print("=" * 60)
    print()
    print(
        f"Components written: {written:,}"
    )
    print(
        f"Output: {OUTPUT_PATH}"
    )

    if components:
        sample = components[0]

        print()
        print("Sample Canonical Component")
        print("-" * 60)
        print(
            sample.model_dump_json(
                indent=2
            )
        )

    print()
    print(
        "Canonical model build complete."
    )
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
