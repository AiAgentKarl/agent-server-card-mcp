# MCP Server Cards

An MCP server for generating, validating, and discovering MCP server cards — a standardized way to describe MCP servers so AI agents can automatically find and understand them.

## What are Server Cards?

Server Cards are machine-readable JSON files that describe an MCP server's capabilities, similar to how `robots.txt` describes crawling rules or `manifest.json` describes web apps. They live at `.well-known/mcp-server-card.json` and contain:

- **Name & Description** — What the server does
- **Tools** — List of available tools with descriptions
- **Author & Repository** — Who built it, where to find the source
- **Categories** — Tags for discovery and search
- **Pricing** — Whether it's free, freemium, or paid
- **Transport** — Whether it uses stdio, HTTP, or both
- **Auth** — Whether authentication is required

## Why Server Cards?

As the MCP ecosystem grows, agents need a way to discover and evaluate servers automatically. Server Cards solve this by providing:

1. **Automatic Discovery** — Agents can check `.well-known/mcp-server-card.json` on any domain
2. **Standardized Metadata** — Consistent format for comparing servers
3. **Capability Description** — Agents know what tools are available before connecting
4. **Trust Signals** — Author, repository, and pricing information

## Installation

```bash
pip install agent-server-card-mcp
```

## Usage

### As MCP Server

```json
{
  "mcpServers": {
    "server-cards": {
      "command": "server-card-server"
    }
  }
}
```

### With uvx

```json
{
  "mcpServers": {
    "server-cards": {
      "command": "uvx",
      "args": ["agent-server-card-mcp"]
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `generate_card` | Generate a `.well-known/mcp-server-card.json` for any MCP server |
| `validate_card` | Validate a server card against the JSON schema |
| `discover` | Try to discover a server card from a URL via `.well-known` |
| `search` | Search indexed server cards by keyword |
| `register` | Register a server card in the local index |
| `schema` | Get the full JSON schema for server cards |

## Server Card Example

```json
{
  "name": "weather-mcp-server",
  "description": "Provides real-time weather data and forecasts",
  "version": "1.0.0",
  "author": "WeatherCorp",
  "repository": "https://github.com/example/weather-mcp",
  "tools": [
    {
      "name": "get_weather",
      "description": "Get current weather for a location"
    },
    {
      "name": "get_forecast",
      "description": "Get 7-day weather forecast"
    }
  ],
  "categories": ["weather", "climate", "data"],
  "pricing": "free",
  "auth_required": false,
  "transport": "stdio"
}
```

## Server Card Schema

Required fields:
- `name` — Unique server name
- `description` — What the server does
- `version` — Semantic version
- `tools` — Array of `{name, description}` objects

Optional but recommended:
- `author` — Author or organization
- `repository` — Source code URL
- `categories` — Tags for searchability
- `pricing` — `free` | `freemium` | `paid` | `open-source`
- `auth_required` — Boolean
- `transport` — `stdio` | `http` | `both`

## How Discovery Works

1. An agent wants to find MCP servers on `example.com`
2. It requests `https://example.com/.well-known/mcp-server-card.json`
3. If the file exists, the agent parses it and learns about available tools
4. The agent can then decide whether to connect based on the metadata

This follows the same pattern as `.well-known/openid-configuration` for OAuth or `.well-known/ai-plugin.json` for ChatGPT plugins.

## License

MIT
