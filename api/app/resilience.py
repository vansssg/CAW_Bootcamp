import random
import time

import pybreaker

from sqlalchemy.exc import OperationalError


class BreakerLogger(pybreaker.CircuitBreakerListener):
    def _state_name(self, cb) -> str:
        state = getattr(cb, "current_state", None)
        name = str(state)
        if "HalfOpen" in name or "half" in name.lower():
            return pybreaker.STATE_HALF_OPEN
        if "Open" in type(state).__name__ and "Half" not in type(state).__name__:
            return pybreaker.STATE_OPEN
        if "Closed" in type(state).__name__:
            return pybreaker.STATE_CLOSED
        return name

    def state_change(self, cb, old_state, new_state):
        from app.main import emit_log

        new_name = str(new_state)
        level = "error" if "Open" in type(new_state).__name__ and "Half" not in type(new_state).__name__ else "info"
        emit_log(
            level,
            "circuit_state_change",
            dependency="postgres",
            old_state=str(old_state),
            new_state=new_name,
        )

    def before_call(self, cb, func, *args, **kwargs):
        from app.main import emit_log

        state = self._state_name(cb)
        if state != pybreaker.STATE_CLOSED:
            emit_log(
                "info",
                "circuit_before_call",
                dependency="postgres",
                circuit_state=state,
            )

    def failure(self, cb, exc):
        from app.main import emit_log

        emit_log(
            "error",
            "circuit_call_failed",
            dependency="postgres",
            circuit_state=self._state_name(cb),
            error_type=type(exc).__name__,
        )

    def success(self, cb):
        from app.main import emit_log

        emit_log(
            "info",
            "circuit_call_succeeded",
            dependency="postgres",
            circuit_state=self._state_name(cb),
        )


db_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=30,
    name="postgres",
    listeners=[BreakerLogger()],
)


def retry_with_backoff(
    fn,
    max_retries: int = 2,
    base_delay: float = 0.1,
    max_delay: float = 2.0,
    jitter: float = 0.05,
    retryable_exceptions: tuple = (ConnectionError, OSError, TimeoutError),
):
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except pybreaker.CircuitBreakerError:
            raise
        except retryable_exceptions as exc:
            last_error = exc
            if attempt == max_retries:
                break
            exponential_delay = min(base_delay * (2**attempt), max_delay)
            delay = max(0.0, exponential_delay + random.uniform(-jitter, jitter))
            from app.main import emit_log

            emit_log(
                "warn",
                "retry_attempt",
                attempt=attempt + 1,
                max_retries=max_retries,
                delay_ms=int(delay * 1000),
                error_type=type(exc).__name__,
            )
            time.sleep(delay)
        except OperationalError:
            raise
    raise last_error
