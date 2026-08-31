from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.repositories.canonical_repository import (
    CanonicalRepository,
)

from backend.app.services.component_query_service import (
    ComponentQueryService,
)

from backend.app.services.recommendation_service import (
    RecommendationService,
)


app = FastAPI(
    title="Engineering Data Query System",
    description=(
        "API for querying, exploring, and visualizing "
        "engineering components."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Application Services
# --------------------------------------------------

repository = CanonicalRepository()

query_service = ComponentQueryService(
    repository
)

recommendation_service = RecommendationService(
    query_service
)


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": (
            "Engineering Data Query System API"
        ),
        "status": "running",
    }


# --------------------------------------------------
# Model Metadata
# --------------------------------------------------

@app.get("/api/model/metadata")
def get_model_metadata():

    return query_service.get_model_metadata()


# --------------------------------------------------
# Get All Components
# --------------------------------------------------

@app.get("/api/components")
def get_components():

    components = query_service.get_all_components()

    return [
        component.model_dump()
        for component in components
    ]


# --------------------------------------------------
# Get Single Component
# --------------------------------------------------

@app.get("/api/components/{component_id}")
def get_component(
    component_id: str,
):

    component = query_service.get_component(
        component_id
    )

    if component is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Component not found: "
                f"{component_id}"
            ),
        )

    return component.model_dump()


# --------------------------------------------------
# Query Components
# --------------------------------------------------

@app.get("/api/query")
def query_components(
    discipline: str | None = None,
    component_type: str | None = None,
    attribute_name: str | None = None,
    attribute_value: str | None = None,
):

    attributes = None

    if (
        attribute_name is not None
        and attribute_value is not None
    ):
        attributes = {
            attribute_name: attribute_value
        }

    components = query_service.query_components(
        discipline=discipline,
        component_type=component_type,
        attributes=attributes,
    )

    return {
        "count": len(components),
        "component_ids": [
            component.component_id
            for component in components
        ],
        "components": [
            component.model_dump()
            for component in components
        ],
    }


# --------------------------------------------------
# Query Recommendations
# --------------------------------------------------

@app.get("/api/recommendations")
def get_recommendations(
    discipline: str | None = None,
    component_type: str | None = None,
    attribute_name: str | None = None,
    attribute_value: str | None = None,
):

    attributes = None

    if (
        attribute_name is not None
        and attribute_value is not None
    ):
        attributes = {
            attribute_name: attribute_value
        }

    recommendation_result = (
        recommendation_service.recommend(
            discipline=discipline,
            component_type=component_type,
            attributes=attributes,
        )
    )

    return recommendation_result


# --------------------------------------------------
# Get Component Connections
# --------------------------------------------------

@app.get(
    "/api/components/{component_id}/connections"
)
def get_component_connections(
    component_id: str,
):

    component = query_service.get_component(
        component_id
    )

    if component is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Component not found: "
                f"{component_id}"
            ),
        )

    connections = (
        query_service.get_component_connections(
            component_id
        )
    )

    return {
        "component_id": component_id,
        "connection_count": len(connections),
        "connections": connections,
    }


# --------------------------------------------------
# 2D Viewer Components
# --------------------------------------------------

@app.get("/api/viewer/components")
def get_viewer_components():

    components = (
        query_service.get_viewer_components()
    )

    return {
        "component_count": len(components),
        "components": components,
    }


# --------------------------------------------------
# Highlighting Data
# --------------------------------------------------

@app.get("/api/highlight")
def get_highlight_components(
    discipline: str | None = None,
    component_type: str | None = None,
    attribute_name: str | None = None,
    attribute_value: str | None = None,
):

    attributes = None

    if (
        attribute_name is not None
        and attribute_value is not None
    ):
        attributes = {
            attribute_name: attribute_value
        }

    component_ids = (
        query_service.get_matching_component_ids(
            discipline=discipline,
            component_type=component_type,
            attributes=attributes,
        )
    )

    return {
        "count": len(component_ids),
        "component_ids": component_ids,
    }