"""
Lokaler JSON-Speicher für Server Cards.

Speichert Server Cards als JSON-Dateien in ~/.mcp-server-cards/
"""

import json
import os
from pathlib import Path
from typing import Optional


# Speicherort: ~/.mcp-server-cards/
STORE_DIR = Path.home() / ".mcp-server-cards"
INDEX_FILE = STORE_DIR / "index.json"


def _ensure_store() -> None:
    """Stellt sicher, dass der Speicherordner existiert."""
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    if not INDEX_FILE.exists():
        INDEX_FILE.write_text(json.dumps({"cards": []}, indent=2))


def _load_index() -> dict:
    """Lädt den Index aus der JSON-Datei."""
    _ensure_store()
    try:
        return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        return {"cards": []}


def _save_index(index: dict) -> None:
    """Speichert den Index in die JSON-Datei."""
    _ensure_store()
    INDEX_FILE.write_text(json.dumps(index, indent=2), encoding="utf-8")


def add_card(card: dict) -> bool:
    """
    Fügt eine Server Card zum Index hinzu.
    Aktualisiert bestehende Cards mit gleichem Namen.

    Returns:
        True wenn neu hinzugefügt, False wenn aktualisiert.
    """
    index = _load_index()
    card_name = card.get("name", "")

    # Prüfe ob Card mit gleichem Namen existiert
    for i, existing in enumerate(index["cards"]):
        if existing.get("name") == card_name:
            index["cards"][i] = card
            _save_index(index)
            return False  # Aktualisiert

    index["cards"].append(card)
    _save_index(index)
    return True  # Neu hinzugefügt


def get_card(name: str) -> Optional[dict]:
    """Gibt eine Server Card nach Name zurück."""
    index = _load_index()
    for card in index["cards"]:
        if card.get("name") == name:
            return card
    return None


def search_cards(query: str) -> list[dict]:
    """
    Durchsucht Server Cards nach einem Suchbegriff.
    Sucht in Name, Beschreibung, Kategorien und Tool-Namen.
    """
    index = _load_index()
    query_lower = query.lower()
    results = []

    for card in index["cards"]:
        # In Name suchen
        if query_lower in card.get("name", "").lower():
            results.append(card)
            continue

        # In Beschreibung suchen
        if query_lower in card.get("description", "").lower():
            results.append(card)
            continue

        # In Kategorien suchen
        categories = card.get("categories", [])
        if any(query_lower in cat.lower() for cat in categories):
            results.append(card)
            continue

        # In Tool-Namen suchen
        tools = card.get("tools", [])
        if any(query_lower in tool.get("name", "").lower() for tool in tools):
            results.append(card)
            continue

        # In Tool-Beschreibungen suchen
        if any(query_lower in tool.get("description", "").lower() for tool in tools):
            results.append(card)
            continue

    return results


def list_all_cards() -> list[dict]:
    """Gibt alle gespeicherten Server Cards zurück."""
    index = _load_index()
    return index["cards"]


def remove_card(name: str) -> bool:
    """
    Entfernt eine Server Card nach Name.

    Returns:
        True wenn entfernt, False wenn nicht gefunden.
    """
    index = _load_index()
    original_count = len(index["cards"])
    index["cards"] = [c for c in index["cards"] if c.get("name") != name]

    if len(index["cards"]) < original_count:
        _save_index(index)
        return True
    return False


def get_store_path() -> str:
    """Gibt den Pfad zum Speicherordner zurück."""
    _ensure_store()
    return str(STORE_DIR)


def get_card_count() -> int:
    """Gibt die Anzahl gespeicherter Cards zurück."""
    index = _load_index()
    return len(index["cards"])
