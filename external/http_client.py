import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class LoggingRetry(Retry):
    """
    Custom Retry class that logs each retry attempt.
    """

    def increment(
        self,
        method=None,
        url=None,
        response=None,
        error=None,
        _pool=None,
        _stacktrace=None,
    ):
        new_retry = super().increment(
            method=method,
            url=url,
            response=response,
            error=error,
            _pool=_pool,
            _stacktrace=_stacktrace,
        )

        reason = response.status if response else error
        logger.warning(
            f"HTTP RETRY: {method} {url} | Reason: {reason} | Remaining: {new_retry.total}"
        )

        return new_retry


def get_retry_session(
    retries=3,
    backoff_factor=1,
    status_forcelist=(500, 502, 503, 504),
    allowed_methods=frozenset(["GET", "HEAD", "OPTIONS"]),
):
    """
    Creates a requests.Session with retry logic.
    Handles retries for both specific status codes and connection/read timeouts.
    """
    session = requests.Session()
    retry = LoggingRetry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=allowed_methods,
        raise_on_status=False,  # Return the response even if it's in the status_forcelist after retries
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


# Shared session with default retry logic (GET only)
_default_session = get_retry_session()


def request(method, url, **kwargs):
    """
    A wrapper around requests.request that provides automatic retries.

    By default, it retries GET requests on timeouts and specific status codes.
    To enable retries for other methods, pass `retry_config` as a dictionary:
    e.g., retry_config={"retries": 5, "allowed_methods": ["GET", "POST"]}
    """
    retry_config = kwargs.pop("retry_config", None)

    # Ensure a default timeout exists to prevent hanging requests
    if "timeout" not in kwargs:
        kwargs["timeout"] = 15

    if retry_config:
        # If specific retry config is provided, create a temporary session
        temp_session = get_retry_session(**retry_config)
        return temp_session.request(method, url, **kwargs)

    return _default_session.request(method, url, **kwargs)
