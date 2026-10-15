"""Tests for gxformat2.options URL resolution."""

from unittest import mock

import pytest

from gxformat2.options import default_url_resolver

TRS_BASE = "https://dockstore.org/api/ga4gh/trs/v2/tools"
ENCODED_DESCRIPTOR_URL = (
    f"{TRS_BASE}/%23workflow%2Fgithub.com%2Fiwc-workflows%2Frnaseq-pe%2Fmain/versions/v1.5/GALAXY/descriptor"
)
TRS_URLS = [
    pytest.param(f"{TRS_BASE}/#workflow/github.com/iwc-workflows/rnaseq-pe/main/versions/v1.5", id="unencoded"),
    pytest.param(f"{TRS_BASE}/%23workflow%2Fgithub.com%2Fiwc-workflows%2Frnaseq-pe%2Fmain/versions/v1.5", id="encoded"),
    pytest.param(
        f"{TRS_BASE}/#workflow/github.com/iwc-workflows/rnaseq-pe/main/versions/v1.5/GALAXY/descriptor",
        id="unencoded-descriptor",
    ),
    pytest.param(ENCODED_DESCRIPTOR_URL, id="encoded-descriptor"),
]


# trs_descriptor_url() itself is covered by the shared declarative case in
# gxformat2/examples/expectations/trs_descriptor_urls.yml.


@pytest.mark.parametrize("url", TRS_URLS)
def test_default_url_resolver_trs(url):
    response = mock.Mock()
    response.json.return_value = {"content": '{"a_galaxy_workflow": "true", "name": "Nested"}'}
    with mock.patch("gxformat2.options.requests.get", return_value=response) as get:
        result = default_url_resolver(url)
    get.assert_called_once_with(ENCODED_DESCRIPTOR_URL, timeout=30)
    assert result == {"a_galaxy_workflow": "true", "name": "Nested"}


def test_default_url_resolver_plain_url():
    response = mock.Mock()
    response.headers = {"content-type": "application/json"}
    response.json.return_value = {"name": "Plain"}
    with mock.patch("gxformat2.options.requests.get", return_value=response) as get:
        result = default_url_resolver("https://example.org/workflow.ga")
    get.assert_called_once_with("https://example.org/workflow.ga", timeout=30)
    assert result == {"name": "Plain"}


def test_default_url_resolver_trs_missing_content():
    response = mock.Mock()
    response.json.return_value = []
    with (
        mock.patch("gxformat2.options.requests.get", return_value=response),
        pytest.raises(ValueError, match="has no string 'content' field"),
    ):
        default_url_resolver(ENCODED_DESCRIPTOR_URL)
