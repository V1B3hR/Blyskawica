"""Error handling utilities for API and external service calls."""

import functools
import logging
import os
import time
from typing import Any, Callable

import requests

logger = logging.getLogger(__name__)


def handle_api_errors(
    default_return: Any = None,
    raise_in_dev: bool = True,
    log_errors: bool = True,
) -> Callable:
    """
    Decorator to handle common API errors gracefully.

    This decorator catches and handles common exceptions from external API calls:
    - Timeouts: Returns default value with warning
    - HTTP errors: Returns default value, logs based on status code
    - Rate limiting (429): Specific handling with warning
    - Generic exceptions: Logs with full traceback, optionally raises in dev

    Args:
        default_return: Value to return on error (default: None)
        raise_in_dev: Re-raise exceptions in development environment (default: True)
        log_errors: Whether to log errors (default: True)

    Returns:
        Decorated function that handles errors gracefully

    Example:
        @handle_api_errors(default_return={}, raise_in_dev=True)
        def fetch_shodan_data(ip: str):
            response = requests.get(f"https://api.shodan.io/shodan/host/{ip}")
            response.raise_for_status()
            return response.json()
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests.Timeout as e:
                if log_errors:
                    logger.warning(f"{func.__name__}: API request timed out - {e}")
                return default_return
            except requests.HTTPError as e:
                if e.response.status_code == 429:
                    if log_errors:
                        logger.warning(
                            f"{func.__name__}: Rate limited by API (429). "
                            f"Consider implementing backoff or reducing request rate."
                        )
                elif e.response.status_code >= 500:
                    if log_errors:
                        logger.error(f"{func.__name__}: Server error (HTTP {e.response.status_code}): {e}")
                elif e.response.status_code >= 400:
                    if log_errors:
                        logger.warning(f"{func.__name__}: Client error (HTTP {e.response.status_code}): {e}")
                else:
                    if log_errors:
                        logger.error(f"{func.__name__}: HTTP error (HTTP {e.response.status_code}): {e}")
                return default_return
            except requests.RequestException as e:
                if log_errors:
                    logger.error(f"{func.__name__}: Request failed - {e}")
                return default_return
            except Exception as e:
                if log_errors:
                    logger.exception(f"{func.__name__}: Unexpected error - {e}")

                # Re-raise in development for debugging
                if raise_in_dev and os.getenv("ENV", "").lower() == "development":
                    raise

                return default_return

        return wrapper

    return decorator


def handle_network_errors(
    default_return: Any = None,
    log_errors: bool = True,
) -> Callable:
    """
    Decorator to handle network-related errors.

    Similar to handle_api_errors but focused on network connectivity issues.

    Args:
        default_return: Value to return on error (default: None)
        log_errors: Whether to log errors (default: True)

    Returns:
        Decorated function that handles network errors

    Example:
        @handle_network_errors(default_return=[])
        def scan_ports(target: str):
            # Network scanning code
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ConnectionError as e:
                if log_errors:
                    logger.error(f"{func.__name__}: Connection error - {e}")
                return default_return
            except TimeoutError as e:
                if log_errors:
                    logger.warning(f"{func.__name__}: Operation timed out - {e}")
                return default_return
            except OSError as e:
                if log_errors:
                    logger.error(f"{func.__name__}: OS error (network-related) - {e}")
                return default_return
            except Exception as e:
                if log_errors:
                    logger.exception(f"{func.__name__}: Unexpected error - {e}")
                return default_return

        return wrapper

    return decorator


class RetryableError(Exception):
    """Exception that indicates an operation should be retried."""

    pass


def retry_on_failure(
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Decorator to retry a function on failure.

    Args:
        retries: Number of retry attempts (default: 3)
        delay: Initial delay between retries in seconds (default: 1.0)
        backoff: Multiplier for delay after each retry (default: 2.0)
        exceptions: Tuple of exceptions to catch (default: (Exception,))

    Returns:
        Decorated function with retry logic

    Example:
        @retry_on_failure(retries=3, delay=1.0, backoff=2.0)
        def unstable_api_call():
            # Code that might fail transiently
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < retries:
                        logger.warning(
                            f"{func.__name__}: Attempt {attempt + 1}/{retries + 1} failed - {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"{func.__name__}: All {retries + 1} attempts failed")

            # If we get here, all retries failed
            if last_exception:
                raise last_exception

        return wrapper

    return decorator
