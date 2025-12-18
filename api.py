"""Simple placeholder for Harvard API fetching.

This file provides an async `fetch_harvard` function used by the Streamlit
app. It currently returns empty lists so the app can run during local
development without requiring network access or an API key. Replace the
implementation with real HTTP calls to the Harvard Art Museums API when
you are ready.
"""
import asyncio
from typing import Tuple, List


async def fetch_harvard(api_key: str, classification: str, max_records: int = 2500) -> Tuple[List, List, List]:
    """Fetch artifact metadata, media and color data for `classification`.

    Args:
        api_key: Your Harvard API key (not used in this placeholder).
        classification: Classification name to query (e.g. "Paintings").
        max_records: Maximum number of records to return.

    Returns:
        A tuple of three lists: (meta, media, colors).
    """

    # Placeholder implementation: return empty lists. Replace with real
    # async HTTP requests (e.g., using `httpx` or `aiohttp`) to collect
    # records from the Harvard Art Museums API.
    await asyncio.sleep(0)  # keep it async
    return [], [], []
