"""HTTP discovery/download helpers with provenance and caching."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import logging
from pathlib import Path
import re
import time
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import requests

LOGGER = logging.getLogger(__name__)

ALLOWED_HOSTS = {
    "www.england.nhs.uk",
    "england.nhs.uk",
    "data.england.nhs.uk",
    "digital.nhs.uk",
    "www.odsdatasearchandexport.nhs.uk",
    "odsdatasearchandexport.nhs.uk",
    "www.ons.gov.uk",
    "ons.gov.uk",
    "www.gov.uk",
    "gov.uk",
    "assets.publishing.service.gov.uk",
}


def _validate_official_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https":
        raise ValueError(f"Only HTTPS source URLs are allowed: {url}")
    host = (parsed.hostname or "").lower().rstrip(".")
    if host not in ALLOWED_HOSTS:
        raise ValueError(f"Source host is not allow-listed: {host or '<missing>'}")


def _secure_session(session: requests.Session | None = None) -> requests.Session:
    sess = session or requests.Session()
    # Do not inherit .netrc credentials or proxy credentials into public-data requests.
    sess.trust_env = False
    return sess


@dataclass(frozen=True)
class DownloadMetadata:
    url: str
    downloaded_at_utc: str
    filename: str
    sha256: str
    bytes: int
    etag: str | None
    last_modified: str | None
    content_type: str | None


def discover_links(page_url: str, pattern: str, session: requests.Session | None = None, timeout: int = 60) -> list[str]:
    """Return unique absolute links from an official publication page matching regex."""
    _validate_official_url(page_url)
    sess = _secure_session(session)
    response = sess.get(page_url, timeout=timeout)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    regex = re.compile(pattern, re.IGNORECASE)
    links: list[str] = []
    for tag in soup.find_all("a", href=True):
        absolute = urljoin(page_url, tag["href"])
        label = f"{tag.get_text(' ', strip=True)} {absolute}"
        if regex.search(label) and absolute not in links:
            links.append(absolute)
    return links


def _safe_filename(url: str) -> str:
    filename = Path(urlparse(url).path).name
    if not filename:
        raise ValueError(f"URL has no filename: {url}")
    return filename


def download_with_cache(
    url: str,
    destination_dir: str | Path,
    metadata_dir: str | Path | None = None,
    timeout: int = 120,
    retries: int = 3,
    session: requests.Session | None = None,
) -> tuple[Path, DownloadMetadata]:
    """Download a file atomically and retain checksum/HTTP provenance.

    A cached file is retained if the remote server reports HTTP 304. ETag and
    Last-Modified are stored when available. The function never fabricates a
    local file when the source cannot be reached.
    """
    _validate_official_url(url)
    destination_dir = Path(destination_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir = Path(metadata_dir or destination_dir / "_metadata")
    metadata_dir.mkdir(parents=True, exist_ok=True)
    filename = _safe_filename(url)
    target = destination_dir / filename
    meta_path = metadata_dir / f"{filename}.json"

    headers = {"User-Agent": "nhs-elective-care-intelligence/1.0 (+public portfolio research)"}
    existing: dict = {}
    if meta_path.exists():
        existing = json.loads(meta_path.read_text(encoding="utf-8"))
        if existing.get("etag"):
            headers["If-None-Match"] = existing["etag"]
        if existing.get("last_modified"):
            headers["If-Modified-Since"] = existing["last_modified"]

    sess = _secure_session(session)
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with sess.get(url, headers=headers, timeout=timeout, stream=True) as response:
                if response.status_code == 304 and target.exists() and existing:
                    return target, DownloadMetadata(**existing)
                response.raise_for_status()
                tmp = target.with_suffix(target.suffix + ".part")
                digest = sha256()
                total = 0
                with tmp.open("wb") as handle:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            handle.write(chunk)
                            digest.update(chunk)
                            total += len(chunk)
                tmp.replace(target)
                meta = DownloadMetadata(
                    url=url,
                    downloaded_at_utc=datetime.now(timezone.utc).isoformat(),
                    filename=filename,
                    sha256=digest.hexdigest(),
                    bytes=total,
                    etag=response.headers.get("ETag"),
                    last_modified=response.headers.get("Last-Modified"),
                    content_type=response.headers.get("Content-Type"),
                )
                meta_path.write_text(json.dumps(asdict(meta), indent=2), encoding="utf-8")
                return target, meta
        except (requests.RequestException, OSError) as exc:
            last_error = exc
            LOGGER.warning("Download attempt %s/%s failed for %s: %s", attempt, retries, url, exc)
            if attempt < retries:
                time.sleep(2 ** (attempt - 1))
    raise RuntimeError(f"Failed to download {url} after {retries} attempts") from last_error
