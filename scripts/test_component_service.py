from pathlib import Path

from backend.app.repositories.sqlite_repository import (
    SQLiteEngineeringRepository,
)

from backend.app.services.component_service import (
    EngineeringComponentService,
)


def main():

    print("=" * 60)
    print("Engineering Component Service Test")
    print("=" * 60)

    project_root = Path(__file__).resolve().parent.parent

    db_path = (
        project_root
        / "data"
        / "generated"
        / "engineering_system.db"
    )

    repository = SQLiteEngineeringRepository(
        db_path
    )

    service = EngineeringComponentService(
        repository
    )

    print()
    print("Building canonical components...")

    components = service.build_components()

    print(
        f"Components created: {len(components):,}"
    )

    print()
    print("-" * 60)
    print("Sample Component")
    print("-" * 60)

    sample = components[0]

    print(
        sample.model_dump_json(
            indent=2
        )
    )

    print()
    print("-" * 60)
    print("Testing component lookup...")
    print("-" * 60)

    component = service.get_component(
        "CMP-100001"
    )

    if component is not None:

        print(
            f"Found component: "
            f"{component.component_id}"
        )

        print(
            f"Type: "
            f"{component.component_type}"
        )

        print(
            f"Discipline: "
            f"{component.discipline}"
        )

    else:

        print("Component not found.")

    print()
    print("=" * 60)
    print("Component Service Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()