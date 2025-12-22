import asyncio
import time
from typing import Callable, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)

class AsyncRateLimiter:
    """
    Token bucket rate limiter for AsyncIO.
    """
    def __init__(self, max_tokens: int, refill_rate: float):
        """
        :param max_tokens: Maximum burst size.
        :param refill_rate: Tokens added per second.
        """
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.refill_rate = refill_rate
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1):
        """
        Wait until sufficient tokens are available.
        """
        async with self._lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.last_refill
                
                # Refill tokens
                refill = elapsed * self.refill_rate
                self.tokens = min(self.max_tokens, self.tokens + refill)
                self.last_refill = now
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                # Calculate wait time
                needed = tokens - self.tokens
                wait_time = needed / self.refill_rate
                await asyncio.sleep(wait_time)

# Common Exception meant to be retried
class RateLimitException(Exception):
    pass

def create_retry_decorator(max_retries: int = 3, min_wait: float = 1, max_wait: float = 10):
    """
    Create a tenacity retry decorator for RateLimitException.
    """
    return retry(
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(RateLimitException),
        reraise=True
    )
