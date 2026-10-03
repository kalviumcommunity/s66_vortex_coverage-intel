"""Context assembly, grounded generation, citations, and guardrails.

FR-11..FR-14 · Spec: specs/06-generation-and-guardrails.md
"""

from .answer import CoverageAnswer, generate  # noqa: F401
from .citations import Citation  # noqa: F401
from .context import assemble  # noqa: F401
from .guardrails import Warning, WarningKind, evaluate  # noqa: F401
