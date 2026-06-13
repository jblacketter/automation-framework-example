"""
Centralized Playwright wait utilities.

All wait patterns in this framework route through `WaitUtils` so timeouts,
polling intervals, and error shapes stay consistent. Page objects delegate
to these methods rather than calling `page.wait_for_*` directly; callers
outside the page layer can import `WaitUtils` and use the same semantics.

Pattern borrowed from `docs/northstar-patterns.md` P9.
"""

from typing import Optional

from playwright.sync_api import Page

from core.config import Config

_FALLBACK_TIMEOUT_MS = 30_000
_DEFAULT_SPINNER_SELECTOR = ".loading, .spinner, [data-loading]"


def _resolve_timeout(timeout_ms: Optional[int]) -> int:
    """Return the caller's explicit timeout or the Config default (ms)."""
    if timeout_ms is not None:
        return timeout_ms
    try:
        cfg = Config()
        # Config exposes timeouts in ms; see core/config.py.
        return int(cfg.default_timeout)
    except Exception:
        return _FALLBACK_TIMEOUT_MS


class WaitUtils:
    """Static wait helpers for the most common Playwright wait patterns.

    All methods accept an optional `timeout_ms`. When omitted, the timeout
    falls back to `Config().default_timeout` (or `Config().navigation_timeout`
    for network-idle), or an internal 30_000 ms default if Config is
    unreachable — so these helpers are safe to call from any layer.
    """

    @staticmethod
    def wait_for_network_idle(page: Page, timeout_ms: Optional[int] = None) -> None:
        """Wait until network activity has been idle for ~500ms.

        Uses Playwright's `wait_for_load_state("networkidle")`. Prefer this
        over a bare `sleep` when you need the page to finish loading.
        """
        if timeout_ms is None:
            try:
                timeout_ms = int(Config().navigation_timeout)
            except Exception:
                timeout_ms = _FALLBACK_TIMEOUT_MS
        page.wait_for_load_state("networkidle", timeout=timeout_ms)

    @staticmethod
    def wait_for_element_visible(
        page: Page, selector: str, timeout_ms: Optional[int] = None
    ) -> None:
        """Wait for an element matching `selector` to become visible."""
        page.wait_for_selector(
            selector, state="visible", timeout=_resolve_timeout(timeout_ms)
        )

    @staticmethod
    def wait_for_element_hidden(
        page: Page, selector: str, timeout_ms: Optional[int] = None
    ) -> None:
        """Wait for an element matching `selector` to become hidden/detached."""
        page.wait_for_selector(
            selector, state="hidden", timeout=_resolve_timeout(timeout_ms)
        )

    @staticmethod
    def wait_for_spinner_gone(
        page: Page,
        selector: str = _DEFAULT_SPINNER_SELECTOR,
        timeout_ms: Optional[int] = None,
    ) -> None:
        """Wait for a loading spinner to disappear.

        Default selector covers common patterns (`.loading`, `.spinner`,
        `[data-loading]`); override with the app's actual indicator when
        the defaults don't match.
        """
        page.wait_for_selector(
            selector, state="hidden", timeout=_resolve_timeout(timeout_ms)
        )
