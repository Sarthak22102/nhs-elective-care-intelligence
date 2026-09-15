import pytest

from nhs_elective_intelligence.ingestion.http import _secure_session, _validate_official_url


def test_official_https_url_is_allowed():
    _validate_official_url("https://www.england.nhs.uk/statistics/example.csv")


def test_http_url_is_rejected():
    with pytest.raises(ValueError, match="Only HTTPS"):
        _validate_official_url("http://www.england.nhs.uk/statistics/example.csv")


def test_non_official_host_is_rejected():
    with pytest.raises(ValueError, match="not allow-listed"):
        _validate_official_url("https://example.com/payload.csv")


def test_session_does_not_use_netrc_or_proxy_environment():
    session = _secure_session()
    assert session.trust_env is False
