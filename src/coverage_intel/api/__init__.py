"""Backend API — FR-15, FR-16.

A guardrail refusal is NOT an error: it returns HTTP 200 with
``status != "grounded"``. An error response must never carry a partial answer
that could be mistaken for a grounded coverage position.

Spec: specs/07-api-contract.md · Phase: phase-07
"""
