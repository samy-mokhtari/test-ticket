from typing import Any

from fastapi.testclient import TestClient


def _get_openapi_schema(
    client: TestClient,
) -> dict[str, Any]:
    """Return the generated OpenAPI schema."""
    response = client.get("/openapi.json")

    assert response.status_code == 200

    return response.json()


def test_api_documentation_is_available(
    client: TestClient,
) -> None:
    for path in (
        "/docs",
        "/redoc",
        "/openapi.json",
    ):
        response = client.get(path)

        assert response.status_code == 200


def test_openapi_schema_contains_api_metadata(
    client: TestClient,
) -> None:
    schema = _get_openapi_schema(client)

    assert schema["info"]["title"] == "Ticket API"
    assert schema["info"]["version"] == "0.1.0"
    assert schema["info"]["summary"] == ("Manage support tickets.")

    tags = {tag["name"]: tag["description"] for tag in schema["tags"]}

    assert "Tickets" in tags
    assert "Health" in tags


def test_openapi_schema_documents_ticket_operations(
    client: TestClient,
) -> None:
    schema = _get_openapi_schema(client)
    paths = schema["paths"]

    expected_operations = {
        ("/tickets/", "post"): "create_ticket",
        ("/tickets/", "get"): "list_tickets",
        (
            "/tickets/{ticket_id}",
            "get",
        ): "get_ticket",
        (
            "/tickets/{ticket_id}",
            "put",
        ): "update_ticket",
        (
            "/tickets/{ticket_id}/close",
            "patch",
        ): "close_ticket",
    }

    for (
        path,
        method,
    ), operation_id in expected_operations.items():
        operation = paths[path][method]

        assert operation["operationId"] == operation_id


def test_openapi_schema_documents_not_found_errors(
    client: TestClient,
) -> None:
    schema = _get_openapi_schema(client)
    paths = schema["paths"]

    operations = [
        paths["/tickets/{ticket_id}"]["get"],
        paths["/tickets/{ticket_id}"]["put"],
        paths["/tickets/{ticket_id}/close"]["patch"],
    ]

    for operation in operations:
        not_found_response = operation["responses"]["404"]
        response_schema = not_found_response["content"]["application/json"][
            "schema"
        ]

        assert response_schema["$ref"] == (
            "#/components/schemas/ErrorResponse"
        )


def test_openapi_schema_contains_ticket_examples(
    client: TestClient,
) -> None:
    schema = _get_openapi_schema(client)
    schemas = schema["components"]["schemas"]

    create_example = schemas["TicketCreate"]["examples"][0]
    update_example = schemas["TicketUpdate"]["examples"][0]

    assert create_example["status"] == "open"
    assert update_example["status"] == "stalled"
