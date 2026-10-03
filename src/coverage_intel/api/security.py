"""Access-key protection for the upload endpoint — FR-16.

The access key is the only application-level control in MVP. Comparison must be
constant-time, and the key is never logged, echoed, or returned.

Spec: specs/07-api-contract.md
"""

from __future__ import annotations

import secrets

from ..config import get_settings
from ..errors import UnauthorizedUpload


def verify_access_key(provided: str | None) -> None:
    """Validate the provided access key or raise UnauthorizedUpload."""
    expected = get_settings().upload_access_key
    if not expected:
        raise UnauthorizedUpload("Upload access key is not configured on this deployment.")
    if not provided or not secrets.compare_digest(provided, expected):
        raise UnauthorizedUpload("Invalid or missing upload access key.")
