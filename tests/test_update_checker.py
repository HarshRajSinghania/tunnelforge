from unittest.mock import MagicMock

import pytest
import requests

from src.core import update_checker
from src.core.update_checker import UpdateChecker


HTML_URL = "https://github.com/sanghyun-io/tunnelforge/releases/tag/v99.0.0"


def _response(payload):
    response = MagicMock()
    response.json.return_value = payload
    return response


@pytest.fixture
def fake_get(monkeypatch):
    get = MagicMock()
    monkeypatch.setattr(update_checker.requests, "get", get)
    return get


def _checker(config_manager=None):
    checker = UpdateChecker(config_manager=config_manager)
    checker.current_version = "2.0.0"
    return checker


def test_newer_tag_needs_update_and_strips_leading_v(fake_get):
    fake_get.return_value = _response({"tag_name": "v99.0.0", "html_url": HTML_URL})

    assert _checker().check_update() == (True, "99.0.0", HTML_URL, None)


@pytest.mark.parametrize("tag", ["v2.0.0", "2.0.0", "v1.9.9"])
def test_same_or_older_tag_does_not_need_update(fake_get, tag):
    fake_get.return_value = _response({"tag_name": tag, "html_url": HTML_URL})

    needs_update, latest, url, error = _checker().check_update()

    assert needs_update is False
    assert latest == tag.lstrip("v")
    assert url == HTML_URL
    assert error is None


@pytest.mark.parametrize("payload", [{}, {"tag_name": ""}, {"tag_name": "v"}])
def test_missing_or_empty_tag_returns_error(fake_get, payload):
    fake_get.return_value = _response(payload)

    needs_update, latest, url, error = _checker().check_update()

    assert (needs_update, latest, url) == (False, None, None)
    assert error


def test_connection_error_returns_error_without_raising(fake_get):
    fake_get.side_effect = requests.exceptions.ConnectionError("unreachable")

    needs_update, latest, url, error = _checker().check_update()

    assert (needs_update, latest, url) == (False, None, None)
    assert "unreachable" in error


def test_non_network_exception_returns_error(fake_get):
    response = MagicMock()
    response.json.side_effect = ValueError("bad json")
    fake_get.return_value = response

    needs_update, latest, url, error = _checker().check_update()

    assert (needs_update, latest, url) == (False, None, None)
    assert "bad json" in error


def test_timeout_defaults_to_five_and_is_passed_to_requests(fake_get):
    fake_get.return_value = _response({"tag_name": "v2.0.0"})
    checker = _checker()

    checker.check_update()

    assert checker.timeout == UpdateChecker.DEFAULT_TIMEOUT == 5
    assert fake_get.call_args.kwargs["timeout"] == 5


def test_timeout_uses_config_manager_value(fake_get):
    fake_get.return_value = _response({"tag_name": "v2.0.0"})
    config = MagicMock()
    config.get_network_timeout_check.return_value = 17
    checker = _checker(config_manager=config)

    checker.check_update()
    checker.get_latest_release_info()

    assert checker.timeout == 17
    assert [c.kwargs["timeout"] for c in fake_get.call_args_list] == [17, 17]


def test_get_latest_release_info_returns_payload(fake_get):
    payload = {"tag_name": "v99.0.0", "html_url": HTML_URL}
    fake_get.return_value = _response(payload)

    assert _checker().get_latest_release_info() == payload


@pytest.mark.parametrize(
    "error",
    [requests.exceptions.ConnectionError("down"), requests.exceptions.Timeout("slow"), ValueError("bad")],
)
def test_get_latest_release_info_returns_none_on_failure(fake_get, error):
    fake_get.side_effect = error

    assert _checker().get_latest_release_info() is None
