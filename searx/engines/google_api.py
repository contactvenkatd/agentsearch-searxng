# SPDX-License-Identifier: AGPL-3.0-or-later
"""Google Programmable Search JSON API engine for AgentSearch."""

import os
import typing as t
from urllib.parse import urlencode

from searx.exceptions import SearxEngineAPIException
from searx.result_types import EngineResults
from searx.utils import html_to_text

if t.TYPE_CHECKING:
    from searx.extended_types import SXNG_Response
    from searx.search.processors import OnlineParams


about = {
    "website": "https://programmablesearchengine.google.com/",
    "wikidata_id": None,
    "official_api_documentation": "https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list",
    "use_official_api": True,
    "require_api_key": True,
    "results": "JSON",
}

categories = ["general", "web"]
paging = False
safesearch = False

base_url = "https://customsearch.googleapis.com/customsearch/v1"

api_key = ""
cse_id = ""


def init(_):
    """Load credentials from the container environment at engine startup."""
    global api_key, cse_id  # pylint: disable=global-statement

    api_key = os.environ.get("GOOGLE_API_KEY", "")
    cse_id = os.environ.get("GOOGLE_CSE_ID", "")
    if not api_key or not cse_id:
        raise SearxEngineAPIException(
            "GOOGLE_API_KEY and GOOGLE_CSE_ID must be configured"
        )


def request(query: str, params: "OnlineParams") -> None:
    """Create a Google Programmable Search JSON API request."""
    params["url"] = base_url + "?" + urlencode(
        {
            "key": api_key,
            "cx": cse_id,
            "q": query,
        }
    )


def response(resp: "SXNG_Response") -> EngineResults:
    """Map a Google JSON response to native SearXNG results."""
    results = EngineResults()
    try:
        data = resp.json()
    except (TypeError, ValueError):
        return results

    if not isinstance(data, dict) or data.get("error"):
        return results

    for item in data.get("items") or []:
        if not isinstance(item, dict):
            continue
        title = item.get("title")
        url = item.get("link")
        if not isinstance(title, str) or not title or not isinstance(url, str) or not url:
            continue
        snippet = item.get("snippet")
        results.add(
            results.types.MainResult(
                title=html_to_text(title),
                url=url,
                content=html_to_text(snippet if isinstance(snippet, str) else ""),
            )
        )

    return results
