from __future__ import annotations

from backend.app.repositories.canonical_repository import (
    CanonicalRepository,
)

from backend.app.services.component_query_service import (
    ComponentQueryService,
)


def main():

    print("=" * 60)
    print("Component Query Service Test")
    print("=" * 60)

    # --------------------------------------------------------
    # Setup
    # --------------------------------------------------------

    repository = CanonicalRepository()

    service = ComponentQueryService(
        repository
    )

    print()
    print(
        f"Canonical components available: "
        f"{repository.get_component_count():,}"
    )

    # --------------------------------------------------------
    # Test 1
    # Get all components
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("Test 1: Get All Components")
    print("-" * 60)

    components = service.get_all_components()

    print(
        f"Components returned: "
        f"{len(components):,}"
    )

    assert len(components) == 1000

    print("PASS")

    # --------------------------------------------------------
    # Test 2
    # Query by discipline
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("Test 2: Query by Discipline")
    print("-" * 60)

    piping_components = service.query_components(
        discipline="Piping"
    )

    print(
        f"Piping components: "
        f"{len(piping_components):,}"
    )

    for component in piping_components[:5]:

        print(
            f"{component.component_id} | "
            f"{component.component_type} | "
            f"{component.zone}"
        )

    assert all(
        component.discipline == "Piping"
        for component in piping_components
    )

    print("PASS")

    # --------------------------------------------------------
    # Test 3
    # Query by component type
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("Test 3: Query by Component Type")
    print("-" * 60)

    valves = service.query_components(
        component_type="Valve"
    )

    print(
        f"Valve components: "
        f"{len(valves):,}"
    )

    for component in valves[:5]:

        print(
            f"{component.component_id} | "
            f"{component.discipline} | "
            f"{component.zone}"
        )

    assert all(
        component.component_type == "Valve"
        for component in valves
    )

    print("PASS")

    # --------------------------------------------------------
    # Test 4
    # Query by attributes
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("Test 4: Query by Engineering Attributes")
    print("-" * 60)

    installed_components = service.query_components(
        attributes={
            "Status": "Installed"
        }
    )

    print(
        f"Installed components: "
        f"{len(installed_components):,}"
    )

    for component in installed_components[:5]:

        print(
            f"{component.component_id} | "
            f"{component.component_type} | "
            f"{component.discipline}"
        )

    assert all(
        component.attributes.get("Status")
        == "Installed"
        for component in installed_components
    )

    print("PASS")

    # --------------------------------------------------------
    # Test 5
    # Combined query
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("Test 5: Combined Query")
    print("-" * 60)

    results = service.query_components(
        discipline="Piping",
        attributes={
            "Status": "Installed"
        }
    )

    print(
        f"Matching components: "
        f"{len(results):,}"
    )

    for component in results[:10]:

        print(
            f"{component.component_id} | "
            f"{component.component_type} | "
            f"Status={component.attributes.get('Status')}"
        )

    assert all(
        component.discipline == "Piping"
        and component.attributes.get("Status")
        == "Installed"
        for component in results
    )

    print("PASS")

    # --------------------------------------------------------
    # Test 6
    # Highlighting IDs
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("Test 6: Highlighting Component IDs")
    print("-" * 60)

    component_ids = (
        service.get_matching_component_ids(
            discipline="Piping",
            attributes={
                "Status": "Installed"
            },
        )
    )

    print(
        f"IDs returned for highlighting: "
        f"{len(component_ids):,}"
    )

    for component_id in component_ids[:10]:

        print(component_id)

    assert len(component_ids) == len(results)

    assert all(
        isinstance(component_id, str)
        for component_id in component_ids
    )

    print("PASS")

    # --------------------------------------------------------
    # Test 7
    # Viewer data
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("Test 7: 2D Viewer Data")
    print("-" * 60)

    viewer_components = (
        service.get_viewer_components()
    )

    print(
        f"Viewer components: "
        f"{len(viewer_components):,}"
    )

    sample = viewer_components[0]

    print()
    print("Sample viewer component:")

    print(
        f"Component ID: "
        f"{sample['component_id']}"
    )

    print(
        f"Type: "
        f"{sample['component_type']}"
    )

    print(
        f"Discipline: "
        f"{sample['discipline']}"
    )

    print(
        f"Geometry: "
        f"{sample['geometry']}"
    )

    assert len(viewer_components) == 1000

    assert "geometry" in sample

    assert "x1" in sample["geometry"]

    assert "y1" in sample["geometry"]

    assert "x2" in sample["geometry"]

    assert "y2" in sample["geometry"]

    print("PASS")

    # --------------------------------------------------------
    # Test 8
    # Component connections
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("Test 8: Component Connections")
    print("-" * 60)

    component_id = "CMP-100001"

    connections = (
        service.get_component_connections(
            component_id
        )
    )

    print(
        f"Component: {component_id}"
    )

    print(
        f"Connections found: "
        f"{len(connections)}"
    )

    for connection in connections:

        print(
            f"{connection['source_uid']} "
            f"→ "
            f"{connection['target_uid']} "
            f"({connection['connection_type']})"
        )

    print("PASS")

    # --------------------------------------------------------
    # Test 9
    # Model metadata
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("Test 9: Model Metadata")
    print("-" * 60)

    metadata = service.get_model_metadata()

    print(
        f"Component count: "
        f"{metadata['component_count']:,}"
    )

    print("Model bounds:")

    for name, value in (
        metadata["bounds"].items()
    ):

        print(
            f"  {name}: {value}"
        )

    assert (
        metadata["component_count"]
        == 1000
    )

    print("PASS")

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("ALL COMPONENT QUERY SERVICE TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()