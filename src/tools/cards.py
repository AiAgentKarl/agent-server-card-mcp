"""
MCP-Tools für Server Card Generierung, Validierung und Discovery.

Definiert das Server Card Schema und stellt Tools bereit für:
- Generierung von .well-known/mcp-server-card.json
- Validierung gegen das Schema
- Discovery über .well-known URLs
- Suche und Registrierung im lokalen Index
"""

import json
from typing import Any

import httpx
import jsonschema

from src.tools.card_store import add_card, search_cards, get_card_count, list_all_cards


# === Server Card JSON Schema ===

SERVER_CARD_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "MCP Server Card",
    "description": "Schema for MCP Server Card — machine-readable metadata for MCP server discovery",
    "type": "object",
    "required": ["name", "description", "version", "tools"],
    "properties": {
        "name": {
            "type": "string",
            "description": "Eindeutiger Name des MCP-Servers",
            "minLength": 1,
            "maxLength": 100,
        },
        "description": {
            "type": "string",
            "description": "Kurze Beschreibung des Servers und seiner Funktionen",
            "minLength": 1,
            "maxLength": 500,
        },
        "version": {
            "type": "string",
            "description": "Semantic Version des Servers (z.B. 1.0.0)",
            "pattern": r"^\d+\.\d+\.\d+",
        },
        "author": {
            "type": "string",
            "description": "Autor oder Organisation",
        },
        "repository": {
            "type": "string",
            "description": "URL zum Source-Code Repository",
            "format": "uri",
        },
        "homepage": {
            "type": "string",
            "description": "URL zur Homepage oder Dokumentation",
            "format": "uri",
        },
        "tools": {
            "type": "array",
            "description": "Liste der verfügbaren MCP-Tools",
            "items": {
                "type": "object",
                "required": ["name", "description"],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name des Tools",
                    },
                    "description": {
                        "type": "string",
                        "description": "Beschreibung was das Tool macht",
                    },
                },
            },
            "minItems": 1,
        },
        "categories": {
            "type": "array",
            "description": "Kategorien/Tags für die Suche",
            "items": {"type": "string"},
        },
        "pricing": {
            "type": "string",
            "description": "Preismodell",
            "enum": ["free", "freemium", "paid", "open-source"],
        },
        "auth_required": {
            "type": "boolean",
            "description": "Ob Authentifizierung benötigt wird",
        },
        "transport": {
            "type": "string",
            "description": "Unterstützter Transport-Typ",
            "enum": ["stdio", "http", "both"],
        },
        "install": {
            "type": "object",
            "description": "Installationsanweisungen",
            "properties": {
                "pip": {"type": "string"},
                "npm": {"type": "string"},
                "docker": {"type": "string"},
            },
        },
        "endpoints": {
            "type": "object",
            "description": "Server-Endpoints für HTTP-Transport",
            "properties": {
                "base_url": {"type": "string", "format": "uri"},
                "health": {"type": "string"},
            },
        },
    },
}


def _build_card(
    name: str,
    description: str,
    tools: list[dict[str, str]],
    version: str = "0.1.0",
    author: str | None = None,
    repo_url: str | None = None,
    categories: list[str] | None = None,
    pricing: str = "free",
    auth_required: bool = False,
    transport: str = "stdio",
) -> dict[str, Any]:
    """Baut ein Server Card Dict aus den Parametern."""
    card: dict[str, Any] = {
        "name": name,
        "description": description,
        "version": version,
        "tools": tools,
    }

    if author:
        card["author"] = author
    if repo_url:
        card["repository"] = repo_url
    if categories:
        card["categories"] = categories

    card["pricing"] = pricing
    card["auth_required"] = auth_required
    card["transport"] = transport

    return card


# === Tool-Funktionen (werden in server.py registriert) ===


async def generate_server_card(
    name: str,
    description: str,
    tools: list[dict[str, str]],
    author: str = "",
    repo_url: str = "",
    version: str = "0.1.0",
    categories: list[str] | None = None,
    pricing: str = "free",
    auth_required: bool = False,
    transport: str = "stdio",
) -> str:
    """
    Generiert eine Server Card im .well-known/mcp-server-card.json Format.

    Args:
        name: Name des MCP-Servers
        description: Beschreibung des Servers
        tools: Liste der Tools [{name, description}, ...]
        author: Autor/Organisation
        repo_url: Repository-URL
        version: Semantic Version (Standard: 0.1.0)
        categories: Kategorien/Tags
        pricing: Preismodell (free/freemium/paid/open-source)
        auth_required: Authentifizierung nötig?
        transport: Transport-Typ (stdio/http/both)

    Returns:
        JSON-String der Server Card
    """
    card = _build_card(
        name=name,
        description=description,
        tools=tools,
        version=version,
        author=author or None,
        repo_url=repo_url or None,
        categories=categories,
        pricing=pricing,
        auth_required=auth_required,
        transport=transport,
    )

    # Validierung
    try:
        jsonschema.validate(instance=card, schema=SERVER_CARD_SCHEMA)
    except jsonschema.ValidationError as e:
        return json.dumps({
            "error": "Generierte Card ist ungültig",
            "detail": str(e.message),
            "path": list(e.absolute_path),
        }, indent=2)

    result = {
        "server_card": card,
        "well_known_path": ".well-known/mcp-server-card.json",
        "instructions": (
            "Platziere diese Datei unter .well-known/mcp-server-card.json "
            "auf deinem Server oder im Repository-Root, damit andere Agents "
            "den Server automatisch entdecken können."
        ),
    }

    return json.dumps(result, indent=2)


async def validate_server_card(card_json: str) -> str:
    """
    Validiert eine Server Card gegen das Schema.

    Args:
        card_json: JSON-String der Server Card

    Returns:
        Validierungsergebnis mit Details
    """
    try:
        card = json.loads(card_json)
    except json.JSONDecodeError as e:
        return json.dumps({
            "valid": False,
            "error": "Ungültiges JSON",
            "detail": str(e),
        }, indent=2)

    errors = []
    try:
        jsonschema.validate(instance=card, schema=SERVER_CARD_SCHEMA)
    except jsonschema.ValidationError as e:
        # Alle Fehler sammeln
        validator = jsonschema.Draft7Validator(SERVER_CARD_SCHEMA)
        for error in validator.iter_errors(card):
            errors.append({
                "message": error.message,
                "path": list(error.absolute_path),
                "schema_path": list(error.absolute_schema_path),
            })

    if errors:
        return json.dumps({
            "valid": False,
            "error_count": len(errors),
            "errors": errors,
        }, indent=2)

    # Zusätzliche Prüfungen (Warnungen)
    warnings = []
    if "author" not in card:
        warnings.append("Kein 'author' angegeben — empfohlen für Vertrauen")
    if "repository" not in card:
        warnings.append("Kein 'repository' angegeben — empfohlen für Transparenz")
    if "categories" not in card:
        warnings.append("Keine 'categories' angegeben — verbessert die Auffindbarkeit")
    if card.get("pricing") is None:
        warnings.append("Kein 'pricing' angegeben — hilft bei der Entscheidungsfindung")

    return json.dumps({
        "valid": True,
        "warnings": warnings if warnings else None,
        "tool_count": len(card.get("tools", [])),
        "name": card.get("name"),
        "version": card.get("version"),
    }, indent=2)


async def discover_server(url: str) -> str:
    """
    Versucht eine Server Card von einer URL zu entdecken.

    Prüft .well-known/mcp-server-card.json auf dem angegebenen Server.

    Args:
        url: Basis-URL des Servers (z.B. https://example.com)

    Returns:
        Gefundene Server Card oder Fehlermeldung
    """
    # URL normalisieren
    base_url = url.rstrip("/")
    if not base_url.startswith(("http://", "https://")):
        base_url = f"https://{base_url}"

    well_known_url = f"{base_url}/.well-known/mcp-server-card.json"

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(well_known_url)

            if response.status_code == 200:
                try:
                    card = response.json()

                    # Validierung
                    try:
                        jsonschema.validate(instance=card, schema=SERVER_CARD_SCHEMA)
                        valid = True
                        validation_errors = []
                    except jsonschema.ValidationError:
                        valid = False
                        validator = jsonschema.Draft7Validator(SERVER_CARD_SCHEMA)
                        validation_errors = [
                            {"message": e.message, "path": list(e.absolute_path)}
                            for e in validator.iter_errors(card)
                        ]

                    return json.dumps({
                        "found": True,
                        "url": well_known_url,
                        "valid": valid,
                        "validation_errors": validation_errors if validation_errors else None,
                        "server_card": card,
                    }, indent=2)

                except json.JSONDecodeError:
                    return json.dumps({
                        "found": True,
                        "url": well_known_url,
                        "valid": False,
                        "error": "Antwort ist kein gültiges JSON",
                    }, indent=2)

            elif response.status_code == 404:
                return json.dumps({
                    "found": False,
                    "url": well_known_url,
                    "message": (
                        f"Keine Server Card unter {well_known_url} gefunden. "
                        "Der Server unterstützt möglicherweise kein .well-known Discovery."
                    ),
                }, indent=2)

            else:
                return json.dumps({
                    "found": False,
                    "url": well_known_url,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}",
                }, indent=2)

    except httpx.ConnectError:
        return json.dumps({
            "found": False,
            "url": well_known_url,
            "error": "Verbindung fehlgeschlagen — Server nicht erreichbar",
        }, indent=2)
    except httpx.TimeoutException:
        return json.dumps({
            "found": False,
            "url": well_known_url,
            "error": "Timeout — Server antwortet nicht rechtzeitig",
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "found": False,
            "url": well_known_url,
            "error": f"Unerwarteter Fehler: {str(e)}",
        }, indent=2)


async def search_server_cards(query: str) -> str:
    """
    Durchsucht den lokalen Index nach Server Cards.

    Args:
        query: Suchbegriff (durchsucht Name, Beschreibung, Kategorien, Tools)

    Returns:
        Gefundene Server Cards
    """
    results = search_cards(query)

    return json.dumps({
        "query": query,
        "result_count": len(results),
        "total_indexed": get_card_count(),
        "results": results,
    }, indent=2)


async def register_server_card(card_json: str) -> str:
    """
    Registriert eine Server Card im lokalen Index.

    Args:
        card_json: JSON-String der Server Card

    Returns:
        Bestätigung oder Fehlermeldung
    """
    try:
        card = json.loads(card_json)
    except json.JSONDecodeError as e:
        return json.dumps({
            "success": False,
            "error": "Ungültiges JSON",
            "detail": str(e),
        }, indent=2)

    # Validierung
    try:
        jsonschema.validate(instance=card, schema=SERVER_CARD_SCHEMA)
    except jsonschema.ValidationError:
        validator = jsonschema.Draft7Validator(SERVER_CARD_SCHEMA)
        errors = [
            {"message": e.message, "path": list(e.absolute_path)}
            for e in validator.iter_errors(card)
        ]
        return json.dumps({
            "success": False,
            "error": "Card entspricht nicht dem Schema",
            "validation_errors": errors,
        }, indent=2)

    # Speichern
    is_new = add_card(card)

    return json.dumps({
        "success": True,
        "action": "registered" if is_new else "updated",
        "name": card.get("name"),
        "total_indexed": get_card_count(),
    }, indent=2)


async def get_card_schema() -> str:
    """
    Gibt das JSON-Schema für Server Cards zurück.

    Returns:
        Das vollständige JSON-Schema
    """
    return json.dumps({
        "schema": SERVER_CARD_SCHEMA,
        "description": (
            "Schema für MCP Server Cards. Pflichtfelder: name, description, "
            "version, tools. Empfohlen: author, repository, categories, pricing."
        ),
        "well_known_path": ".well-known/mcp-server-card.json",
    }, indent=2)
