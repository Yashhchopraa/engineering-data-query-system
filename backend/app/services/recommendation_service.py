from __future__ import annotations

from collections import Counter
from typing import Any

from backend.app.services.component_query_service import (
    ComponentQueryService,
)


class RecommendationService:
    """
    Intelligent recommendation service for engineering queries.

    The service analyzes user filters and generates
    alternative recommendations when an exact query
    returns few or no matching components.
    """

    MIN_RESULTS_FOR_RECOMMENDATIONS = 5 
    
    def __init__(
        self,
        query_service: ComponentQueryService,
    ) -> None:

        self.query_service = query_service

    def recommend(
        self,
        component_type: str | None = None,
        discipline: str | None = None,
        zone: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze a query and generate recommendations.

        Returns:
        - exact match count
        - exact matching component IDs
        - filter relaxation suggestions
        - alternative attribute values
        """

        if attributes is None:
            attributes = {}

        # --------------------------------------------------
        # 1. Execute the exact query
        # --------------------------------------------------

        exact_results = (
            self.query_service.query_components(
                component_type=component_type,
                discipline=discipline,
                zone=zone,
                attributes=attributes,
            )
        )

        recommendations = []
        if (
            len(exact_results)
            > self.MIN_RESULTS_FOR_RECOMMENDATIONS
        ):
            return {
                "exact_match_count": len(
                    exact_results
                ),

                "exact_component_ids": [
                    component.component_id
                    for component in exact_results
                ],

                "recommendation_count": 0,

                "recommendations": [],
            }
        # --------------------------------------------------
        # 2. Test relaxing semantic filters
        # --------------------------------------------------

        semantic_filters = {
            "component_type": component_type,
            "discipline": discipline,
            "zone": zone,
        }

        for filter_name, filter_value in (
            semantic_filters.items()
        ):

            if filter_value is None:
                continue

            relaxed_component_type = component_type
            relaxed_discipline = discipline
            relaxed_zone = zone

            if filter_name == "component_type":
                relaxed_component_type = None

            elif filter_name == "discipline":
                relaxed_discipline = None

            elif filter_name == "zone":
                relaxed_zone = None

            relaxed_results = (
                self.query_service.query_components(
                    component_type=relaxed_component_type,
                    discipline=relaxed_discipline,
                    zone=relaxed_zone,
                    attributes=attributes,
                )
            )

            if len(relaxed_results) > len(
                exact_results
            ):

                recommendations.append(
                    {
                        "type": "relax_filter",
                        "filter": filter_name,
                        "current_value": filter_value,
                        "message": (
                            f"Try removing the "
                            f"{filter_name} filter"
                        ),
                        "result_count": len(
                            relaxed_results
                        ),
                    }
                )

        # --------------------------------------------------
        # 3. Test relaxing engineering attributes
        # --------------------------------------------------

        for attribute_name, attribute_value in (
            attributes.items()
        ):

            relaxed_attributes = dict(attributes)

            del relaxed_attributes[
                attribute_name
            ]

            relaxed_results = (
                self.query_service.query_components(
                    component_type=component_type,
                    discipline=discipline,
                    zone=zone,
                    attributes=relaxed_attributes,
                )
            )

            if len(relaxed_results) > len(
                exact_results
            ):

                recommendations.append(
                    {
                        "type": "relax_attribute",
                        "attribute": attribute_name,
                        "current_value": attribute_value,
                        "message": (
                            f"Try removing the "
                            f"{attribute_name} filter"
                        ),
                        "result_count": len(
                            relaxed_results
                        ),
                    }
                )

        # --------------------------------------------------
        # 4. Find alternative values for attributes
        # --------------------------------------------------

        for attribute_name, attribute_value in (
            attributes.items()
        ):

            base_attributes = dict(attributes)

            del base_attributes[
                attribute_name
            ]

            base_results = (
                self.query_service.query_components(
                    component_type=component_type,
                    discipline=discipline,
                    zone=zone,
                    attributes=base_attributes,
                )
            )

            value_counter = Counter()

            for component in base_results:

                for actual_name, actual_value in (
                    component.attributes.items()
                ):

                    if (
                        actual_name.lower()
                        == attribute_name.lower()
                    ):

                        if (
                            str(actual_value).lower()
                            != str(attribute_value).lower()
                        ):

                            value_counter[
                                actual_value
                            ] += 1

            for suggested_value, count in (
                value_counter.most_common(3)
            ):

                recommendations.append(
                    {
                        "type": "alternative_value",
                        "attribute": attribute_name,
                        "current_value": attribute_value,
                        "suggested_value": (
                            suggested_value
                        ),
                        "message": (
                            f"Try {attribute_name}="
                            f"{suggested_value}"
                        ),
                        "result_count": count,
                    }
                )

        # --------------------------------------------------
        # 5. Return structured recommendation response
        # --------------------------------------------------

        return {
            "exact_match_count": len(
                exact_results
            ),

            "exact_component_ids": [
                component.component_id
                for component in exact_results
            ],

            "recommendation_count": len(
                recommendations
            ),

            "recommendations": recommendations,
        }