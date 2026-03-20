"""
MCP Server für Server Card Discovery und Management.

Ermöglicht AI-Agents das Generieren, Validieren und Entdecken von
MCP Server Cards über das .well-known/mcp-server-card.json Protokoll.
"""

from mcp.server.fastmcp import FastMCP

from src.tools.cards import (
    generate_server_card,
    validate_server_card,
    discover_server,
    search_server_cards,
    register_server_card,
    get_card_schema,
)

# Server-Instanz
mcp = FastMCP(
    "server-card-mcp",
    instructions=(
        "MCP Server für Server Card Discovery. Generiert, validiert und "
        "entdeckt MCP Server Cards über das .well-known/mcp-server-card.json "
        "Protokoll. Ermöglicht Agents, andere MCP-Server automatisch zu finden "
        "und deren Fähigkeiten zu verstehen."
    ),
)


# === Tools registrieren ===


@mcp.tool()
async def generate_card(
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
    Generate a .well-known/mcp-server-card.json for an MCP server.

    Erstellt eine maschinenlesbare Server Card mit allen Metadaten,
    die andere Agents zur automatischen Discovery brauchen.

    Args:
        name: Name des MCP-Servers
        description: Kurze Beschreibung des Servers
        tools: Liste der Tools als [{name: "tool_name", description: "was es tut"}, ...]
        author: Autor oder Organisation
        repo_url: URL zum Repository
        version: Semantic Version (Standard: 0.1.0)
        categories: Tags/Kategorien für die Suche
        pricing: Preismodell (free/freemium/paid/open-source)
        auth_required: Ob Authentifizierung benötigt wird
        transport: Transport-Typ (stdio/http/both)
    """
    return await generate_server_card(
        name=name,
        description=description,
        tools=tools,
        author=author,
        repo_url=repo_url,
        version=version,
        categories=categories,
        pricing=pricing,
        auth_required=auth_required,
        transport=transport,
    )


@mcp.tool()
async def validate_card(card_json: str) -> str:
    """
    Validate a server card JSON against the schema.

    Prüft ob eine Server Card alle Pflichtfelder enthält und
    dem Schema entspricht. Gibt auch Warnungen für fehlende
    empfohlene Felder.

    Args:
        card_json: JSON-String der Server Card
    """
    return await validate_server_card(card_json)


@mcp.tool()
async def discover(url: str) -> str:
    """
    Discover an MCP server card from a URL via .well-known.

    Prüft ob unter der angegebenen URL eine Server Card unter
    .well-known/mcp-server-card.json verfügbar ist.

    Args:
        url: Basis-URL des Servers (z.B. https://example.com)
    """
    return await discover_server(url)


@mcp.tool()
async def search(query: str) -> str:
    """
    Search indexed server cards by keyword.

    Durchsucht den lokalen Index nach Server Cards.
    Sucht in Name, Beschreibung, Kategorien und Tool-Namen.

    Args:
        query: Suchbegriff
    """
    return await search_server_cards(query)


@mcp.tool()
async def register(card_json: str) -> str:
    """
    Register a server card in the local index.

    Fügt eine Server Card zum lokalen Index hinzu oder aktualisiert
    eine bestehende Card mit gleichem Namen.

    Args:
        card_json: JSON-String der Server Card
    """
    return await register_server_card(card_json)


@mcp.tool()
async def schema() -> str:
    """
    Get the JSON schema for MCP server cards.

    Gibt das vollständige Schema zurück, das beschreibt welche Felder
    eine Server Card haben kann und welche Pflicht sind.
    """
    return await get_card_schema()


def main():
    """Startet den MCP-Server."""
    mcp.run()


if __name__ == "__main__":
    main()
