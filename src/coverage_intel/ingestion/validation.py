"""Corpus-wide ingestion validation and completeness reporting."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from pydantic import BaseModel, Field

from coverage_intel.errors import CoverageIntelError, ExtractionError

from .cleaning import clean
from .loaders import ExtractedDocument, load


class ValidationFailure(BaseModel):
    """A source that could not enter the prepared corpus."""

    path: str
    code: str
    message: str


class CorpusValidationReport(BaseModel):
    """Completeness result for one corpus preparation run."""

    total: int
    indexed: int
    failed: int
    failures: list[ValidationFailure] = Field(default_factory=list)
    target_success_rate: float = 0.95

    @property
    def success_rate(self) -> float:
        """Return the indexed fraction, or zero for an empty corpus."""
        return self.indexed / self.total if self.total else 0.0

    @property
    def meets_target(self) -> bool:
        """Whether the corpus reached its configured ingestion target."""
        return self.total > 0 and self.success_rate >= self.target_success_rate


def prepare_corpus(
    paths: Iterable[Path], *, target_success_rate: float = 0.95
) -> tuple[list[ExtractedDocument], CorpusValidationReport]:
    """Load and clean every source, returning usable documents and a report."""
    if not 0.0 <= target_success_rate <= 1.0:
        raise ValueError("target_success_rate must be between 0.0 and 1.0")

    prepared: list[ExtractedDocument] = []
    failures: list[ValidationFailure] = []
    path_list = list(paths)
    for path in path_list:
        try:
            document = load(path)
            cleaned = clean(document.blocks)
            if not cleaned:
                raise ExtractionError(f"No usable text remains after cleaning: {path.name}")
            char_count = sum(len(block.text) for block in cleaned)
            prepared.append(document.model_copy(update={"blocks": cleaned, "char_count": char_count}))
        except CoverageIntelError as exc:
            failures.append(
                ValidationFailure(path=str(path), code=exc.error_code, message=str(exc))
            )
        except (OSError, ValueError) as exc:
            failures.append(
                ValidationFailure(path=str(path), code="INGESTION_ERROR", message=str(exc))
            )

    report = CorpusValidationReport(
        total=len(path_list),
        indexed=len(prepared),
        failed=len(failures),
        failures=failures,
        target_success_rate=target_success_rate,
    )
    return prepared, report
