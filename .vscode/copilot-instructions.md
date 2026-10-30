# Agent Notes

## Project Shape

- This is a Python 3.11+ smart-home lighting controller for a Raspberry Pi. See [README.md](README.md) for the short project description.
- The main service is the async Flask/Hypercorn app in [app.py](app.py). It handles Sleep as Android webhooks, direct light-control POSTs, mutable config updates, and starts an APScheduler periodic check.
- Device access is layered through wrappers: [wrappers/base.py](wrappers/base.py) defines the shared contract, [wrappers/bulb_wrapper.py](wrappers/bulb_wrapper.py) controls the Wiz bulb, [wrappers/WLED_wrapper.py](wrappers/WLED_wrapper.py) controls WLED, and [wrappers/all.py](wrappers/all.py) fans operations out to enabled devices.
- Lighting behavior belongs in [lighting_routines.py](lighting_routines.py) and periodic color-temperature behavior in [periodic_tasks.py](periodic_tasks.py), not in route handlers.
- Device addresses and metadata come from [objects.yaml](objects.yaml). Runtime feature toggles and timestamps persist through [utils/json_wrapper.py](utils/json_wrapper.py) using [utils/mutable_globals.json](utils/mutable_globals.json).

## Commands

- Install/sync dependencies with `uv sync`.
- Run tests with `uv run pytest`.
- Run focused tests with `uv run pytest tests/test_bulb_wrapper.py` or another specific test file.
- Lint with `uv run ruff check .`.
- Start the app locally with `uv run app.py`; the Raspberry Pi startup scripts are [start.sh](start.sh) and [scripts/start_server.sh](scripts/start_server.sh).

## Coding Conventions

- Preserve the async style. Device operations are `async def`, and multi-device orchestration uses `asyncio.TaskGroup` in [wrappers/all.py](wrappers/all.py).
- Keep Flask route handlers thin. Parse/validate request data there, then call routines or wrappers for actual behavior.
- Prefer the shared wrapper API (`turn_on`, `turn_off`, `toggle`, `is_on`, `is_connected`) over reaching directly into device libraries from app or routine code.
- Use `utils.get_logger.get_logger` for logging and keep log messages useful for a headless Raspberry Pi service.
- When adding user-tunable runtime state, update the Pydantic model in [extra_types.py](extra_types.py), the wrapper properties in [utils/json_wrapper.py](utils/json_wrapper.py), and any route/config handling together.

## Testing Guidance

- Tests are pytest-based. Async tests use `pytest.mark.asyncio`; external hardware/network calls should be mocked with `mocker`, `AsyncMock`, `responses`, or equivalent fixtures.
- Do not require real Wiz bulbs, WLED strips, fixed LAN IPs, or Raspberry Pi-only shell behavior for tests.
- Add focused tests near the affected behavior: wrapper behavior in [tests/test_bulb_wrapper.py](tests/test_bulb_wrapper.py) or [tests/test_wrapper.py](tests/test_wrapper.py), mutable config helpers in [tests/test_utils.py](tests/test_utils.py), and UDP packet decoding in [tests/test_UDP_sync.py](tests/test_UDP_sync.py).

## Project Pitfalls

- `utils.mutable_globals` points at the real [utils/mutable_globals.json](utils/mutable_globals.json). Tests should use temporary files or mocks when mutating global state.
- `MutableGlobalsWrapper.use_wled` currently returns `False` unconditionally in [utils/json_wrapper.py](utils/json_wrapper.py), so WLED paths may be disabled even if the JSON value says otherwise.
- Some wrapper methods intentionally catch broad device exceptions and log failures instead of raising. Check the existing behavior before changing exception flow.
- The shell scripts target Linux/Raspberry Pi environments; on Windows, prefer `uv run ...` commands from PowerShell.