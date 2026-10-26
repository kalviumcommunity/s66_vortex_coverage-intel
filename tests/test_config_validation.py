import pytest

from coverage_intel.config import Settings


def test_settings_reject_invalid_runtime_limits() -> None:
    with pytest.raises(ValueError, match="TCP port"):
        Settings(api_port=0)
