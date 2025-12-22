import asyncio
import time
import pytest
from unittest.mock import Mock
from app.utils.rate_limiter import AsyncRateLimiter, create_retry_decorator, RateLimitException
from tenacity import RetryError

@pytest.mark.asyncio
async def test_async_rate_limiter_acquire():
    # 5 tokens, refill 10 per second
    limiter = AsyncRateLimiter(max_tokens=5, refill_rate=10)
    
    start = time.monotonic()
    # Consume 5 tokens immediately
    await limiter.acquire(5)
    duration = time.monotonic() - start
    
    # Should be instant
    assert duration < 0.1
    
    # Next token should wait ~0.1s
    start = time.monotonic()
    await limiter.acquire(1)
    duration = time.monotonic() - start
    
    assert duration >= 0.08 # Allow slight tolerance

@pytest.mark.asyncio
async def test_async_rate_limiter_burst_limit():
    limiter = AsyncRateLimiter(max_tokens=2, refill_rate=1)
    
    await limiter.acquire(2)
    assert limiter.tokens < 1
    
    start = time.monotonic()
    await limiter.acquire(1) # Should wait ~1s
    duration = time.monotonic() - start
    
    assert duration > 0.9

@pytest.mark.asyncio
async def test_retry_decorator_success():
    decorator = create_retry_decorator(max_retries=3, min_wait=0.01, max_wait=0.1)
    
    mock_func = Mock(return_value="Success")
    
    @decorator
    async def run():
        return mock_func()
        
    result = await run()
    assert result == "Success"
    assert mock_func.call_count == 1

@pytest.mark.asyncio
async def test_retry_decorator_fail_eventually():
    decorator = create_retry_decorator(max_retries=2, min_wait=0.01, max_wait=0.1)
    
    mock_func = Mock(side_effect=RateLimitException("Too many requests"))
    
    @decorator
    async def run():
        return mock_func()
        
    with pytest.raises(RateLimitException):
        await run()
    
    # Should be called 2 times (try 1 + retry 1 = 2 attempts total permitted by stop_after_attempt(2)?) 
    # tenacity stop_after_attempt(n) means n attempts total.
    assert mock_func.call_count == 2
