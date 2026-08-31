from backend.app.repositories.canonical_repository import (
    CanonicalRepository,
)


def main() -> None:

    print("=" * 60)
    print("Canonical Repository Test")
    print("=" * 60)

    repository = CanonicalRepository()

    print()
    print(
        f"Components loaded: "
        f"{repository.get_component_count():,}"
    )

    print()
    print("Model bounds:")

    bounds = repository.get_model_bounds()

    for key, value in bounds.items():
        print(f"  {key}: {value}")

    print()
    print("Testing component lookup...")

    component = repository.get_component_by_id(
        "CMP-100001"
    )

    if component is None:
        print("Component not found.")
        return

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

    print()
    print("Repository test complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()