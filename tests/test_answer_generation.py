from coverage_intel.generation.answer import AnswerStatus, generate
from coverage_intel.generation.context import Context


def test_generation_refuses_to_answer_without_evidence() -> None:
    answer = generate("Is this covered?", Context(text="", blocks=[], token_count=0), "q-1")
    assert answer.status is AnswerStatus.INSUFFICIENT_EVIDENCE
