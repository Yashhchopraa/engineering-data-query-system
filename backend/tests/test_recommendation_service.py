from backend.app.repositories.canonical_repository import (
    CanonicalRepository,
)
from backend.app.services.component_query_service import (
    ComponentQueryService,
)
from backend.app.services.recommendation_service import (
    RecommendationService,
)


def print_recommendations(
    result: dict,
) -> None:

    print()

    print(
        f"Exact matches: "
        f"{result['exact_match_count']}"
    )

    print(
        f"Recommendations: "
        f"{result['recommendation_count']}"
    )

    print()

    for index, recommendation in enumerate(
        result["recommendations"],
        start=1,
    ):

        print(
            f"{index}. "
            f"{recommendation['message']}"
        )

        print(
            f"   Type: "
            f"{recommendation['type']}"
        )

        print(
            f"   Result count: "
            f"{recommendation['result_count']}"
        )

        print()


def main():

    print("=" * 60)

    print(
        "Engineering Recommendation Service Test"
    )

    print("=" * 60)

    repository = CanonicalRepository()

    query_service = ComponentQueryService(
        repository
    )

    recommendation_service = RecommendationService(
        query_service
    )

    # --------------------------------------------------
    # Test 1
    # Impossible / highly restrictive query
    # --------------------------------------------------

    print()

    print("-" * 60)

    print(
        "Test 1: Restrictive Engineering Query"
    )

    print("-" * 60)

    result = recommendation_service.recommend(
        discipline="Piping",
        component_type="Valve",
        attributes={
            "Status": "Installed",
            "Material": "Titanium",
        },
    )

    print_recommendations(result)

    # --------------------------------------------------
    # Test 2
    # Existing query with exact matches
    # --------------------------------------------------

    print("-" * 60)

    print(
        "Test 2: Existing Engineering Query"
    )

    print("-" * 60)

    result = recommendation_service.recommend(
        discipline="Piping",
        component_type="Valve",
        attributes={
            "Status": "Installed",
        },
    )

    print_recommendations(result)

    print("=" * 60)

    print(
        "Recommendation Service Test Complete"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()