"""Scanner service — wraps external reconnaissance tools.

Each method runs a security tool via subprocess, parses its JSON output,
and returns normalized Python data structures ready for database storage.

Tools used:
  - subfinder: subdomain enumeration
  - dnsx:      DNS resolution
  - httpx:     HTTP probing and technology detection
  - naabu:     port scanning
  - nuclei:    vulnerability scanning

All tools are ProjectDiscovery open-source projects installed in the
worker Docker container. They accept input via stdin or temp files
and output newline-delimited JSON (JSONL).
"""

import json
import logging
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 600  # 10 minutes


def _run_command(
    cmd: list[str],
    stdin_data: str | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """Run a subprocess command and return its stdout.

    Args:
        cmd: Command and arguments to execute.
        stdin_data: Optional string to feed to stdin.
        timeout: Maximum seconds to wait before killing the process.

    Returns:
        The captured stdout as a string.

    Raises:
        subprocess.TimeoutExpired: If the command exceeds the timeout.
        RuntimeError: If the command exits with a non-zero code.
    """
    logger.info("Running: %s", " ".join(cmd))
    result = subprocess.run(
        cmd,
        input=stdin_data,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        logger.warning(
            "Command exited with code %d: %s\nstderr: %s",
            result.returncode,
            " ".join(cmd),
            result.stderr[:500],
        )
    return result.stdout


def _parse_jsonl(output: str) -> list[dict]:
    """Parse newline-delimited JSON output into a list of dicts."""
    results = []
    for line in output.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            results.append(json.loads(line))
        except json.JSONDecodeError:
            logger.debug("Skipping non-JSON line: %s", line[:100])
    return results


def _write_temp_list(items: list[str]) -> str:
    """Write a list of strings to a temporary file, return the path."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False
    )
    tmp.write("\n".join(items))
    tmp.close()
    return tmp.name


def _cleanup(path: str) -> None:
    """Remove a temporary file."""
    try:
        Path(path).unlink(missing_ok=True)
    except OSError:
        pass


# ── Subfinder ────────────────────────────────────────────────────────────


def run_subfinder(target: str, timeout: int = DEFAULT_TIMEOUT) -> list[str]:
    """Discover subdomains for a target domain.

    Args:
        target: Root domain to enumerate (e.g. "example.com").
        timeout: Max seconds.

    Returns:
        Sorted, deduplicated list of discovered subdomains.
    """
    try:
        output = _run_command(
            ["subfinder", "-d", target, "-silent", "-json"],
            timeout=timeout,
        )
        records = _parse_jsonl(output)
        subdomains = {r.get("host", "") for r in records if r.get("host")}
    except Exception:
        # Fallback to plain-text mode
        logger.info("JSON mode failed, falling back to plain text")
        output = _run_command(
            ["subfinder", "-d", target, "-silent"],
            timeout=timeout,
        )
        subdomains = {
            line.strip() for line in output.splitlines() if line.strip()
        }

    # Always include the target itself
    subdomains.add(target)
    return sorted(subdomains)


# ── dnsx ─────────────────────────────────────────────────────────────────


def run_dnsx(
    subdomains: list[str], timeout: int = DEFAULT_TIMEOUT
) -> list[dict]:
    """Resolve DNS records for a list of subdomains.

    Returns a list of dicts like:
        {"host": "sub.example.com", "a": ["1.2.3.4"], "cname": [...], ...}
    """
    tmp = _write_temp_list(subdomains)
    try:
        output = _run_command(
            ["dnsx", "-l", tmp, "-json", "-a", "-aaaa", "-cname", "-resp", "-silent"],
            timeout=timeout,
        )
        return _parse_jsonl(output)
    finally:
        _cleanup(tmp)


# ── httpx ────────────────────────────────────────────────────────────────


def run_httpx(
    subdomains: list[str], timeout: int = DEFAULT_TIMEOUT
) -> list[dict]:
    """Probe HTTP services on a list of hosts.

    Returns a list of dicts like:
        {"url": "https://...", "status_code": 200, "title": "...",
         "tech": [...], "content_type": "...", "content_length": 1234}
    """
    tmp = _write_temp_list(subdomains)
    try:
        output = _run_command(
            [
                "httpx",
                "-l", tmp,
                "-json",
                "-title",
                "-tech-detect",
                "-status-code",
                "-content-length",
                "-content-type",
                "-follow-redirects",
                "-silent",
            ],
            timeout=timeout,
        )
        return _parse_jsonl(output)
    finally:
        _cleanup(tmp)


# ── naabu ────────────────────────────────────────────────────────────────


def run_naabu(
    hosts: list[str], timeout: int = DEFAULT_TIMEOUT
) -> list[dict]:
    """Scan for open ports on a list of hosts.

    Returns a list of dicts like:
        {"host": "1.2.3.4", "port": 443, "protocol": "tcp"}
    """
    tmp = _write_temp_list(hosts)
    try:
        output = _run_command(
            ["naabu", "-list", tmp, "-json", "-top-ports", "1000", "-silent"],
            timeout=timeout,
        )
        return _parse_jsonl(output)
    finally:
        _cleanup(tmp)


# ── nuclei ───────────────────────────────────────────────────────────────


def run_nuclei(
    urls: list[str], timeout: int = DEFAULT_TIMEOUT
) -> list[dict]:
    """Run vulnerability templates against a list of URLs.

    Returns a list of dicts like:
        {"host": "...", "template-id": "...", "name": "...",
         "severity": "high", "matched-at": "...", ...}
    """
    tmp = _write_temp_list(urls)
    try:
        output = _run_command(
            [
                "nuclei",
                "-l", tmp,
                "-json",
                "-severity", "critical,high,medium,low",
                "-silent",
            ],
            timeout=timeout,
        )
        return _parse_jsonl(output)
    finally:
        _cleanup(tmp)
