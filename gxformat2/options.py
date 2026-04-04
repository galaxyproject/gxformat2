"""Conversion options and URL resolution for workflow format conversion."""

from __future__ import annotations

import base64
import re
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import requests
import yaml

StateEncodeToNativeFn = Optional[Callable[[dict, Dict[str, Any]], Optional[Dict[str, Any]]]]
"""Callback to encode format2 state back to native tool_state.

Accepts (step, state) where step is the partially-built native step dict
and state is the format2 state dict after setup_connected_values processing.
Returns {param_name: encoded_value} as clean dicts for native tool_state,
or None to fall back to default dict passthrough (no JSON encoding).
"""

StateEncodeToFormat2Fn = Optional[Callable[[dict], Optional[Dict[str, Any]]]]
"""Callback to convert a native tool step's tool_state to format2 state.

Accepts a native step dict (with tool_id, tool_version, tool_state).
Returns a format2 state dict, or None to fall back to default tool_state passthrough.
"""

UrlResolverFn = Optional[Callable[[str], dict[str, Any]]]
"""Callback to fetch a URL and return a parsed workflow dict.

Accepts a URL string, returns a parsed dict (native or format2).
Galaxy provides its own with allowlists/policy; gxformat2 provides
a default via :func:`default_url_resolver`.
"""

TRS_URL_REGEX = re.compile(
    r"(?P<trs_base_url>https?://.+)/ga4gh/trs/v2/tools/(?P<tool_id>.+)/versions/(?P<version_id>[^/]+)"
)
MAX_EXPANSION_DEPTH = 10


class ConversionOptions:
    """Options for workflow format conversion and expansion.

    Controls native↔Format2 conversion, subworkflow expansion,
    and URL resolution.
    """

    def __init__(  # noqa: D107
        self,
        workflow_directory: str | Path | None = None,
        encode_tool_state_json: bool = True,
        deduplicate_subworkflows: bool = False,
        state_encode_to_native: StateEncodeToNativeFn = None,
        state_encode_to_format2: StateEncodeToFormat2Fn = None,
        compact: bool = False,
        url_resolver: UrlResolverFn = None,
        strict_structure: bool = False,
    ):
        self.workflow_directory = str(workflow_directory) if workflow_directory else None
        self.encode_tool_state_json = encode_tool_state_json
        self.deduplicate_subworkflows = deduplicate_subworkflows
        self.state_encode_to_native = state_encode_to_native
        self.state_encode_to_format2 = state_encode_to_format2
        self.compact = compact
        self.url_resolver = url_resolver
        self.strict_structure = strict_structure


def default_url_resolver(url: str) -> dict[str, Any]:
    """Fetch a URL and return a parsed workflow dict.

    Handles:
    - ``base64://`` URLs: base64-decode inline content
    - TRS URLs (GA4GH pattern): fetch descriptor endpoint, extract ``content``
    - Plain URLs: HTTP GET, parse as YAML/JSON
    """
    if url.startswith("base64://"):
        content = base64.b64decode(url[len("base64://") :]).decode("utf-8")
        return yaml.safe_load(content)

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    if is_trs_url(url):
        descriptor = response.json()
        return yaml.safe_load(descriptor["content"])

    content_type = response.headers.get("content-type", "")
    if "json" in content_type:
        return response.json()
    return yaml.safe_load(response.text)


def is_trs_url(url: str) -> bool:
    """Check if a URL matches the GA4GH TRS v2 tools/versions pattern."""
    return bool(TRS_URL_REGEX.match(url))
