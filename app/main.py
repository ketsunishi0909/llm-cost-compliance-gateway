from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(
    title="LLM Cost & Compliance Gateway",
    version="0.1.0",
)

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}(?!\d)")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


class GatewayRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=50000)
    expected_complexity: Literal["low", "medium", "high"] | None = None


class GatewayResponse(BaseModel):
    redacted_prompt: str
    route: Literal["small", "standard", "premium"]
    pii_types: list[str]
    cache_status: Literal["not_checked"]
    provider_called: bool


def redact_pii(text: str) -> tuple[str, list[str]]:
    pii_types: list[str] = []

    if EMAIL_RE.search(text):
        pii_types.append("email")
        text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)

    if PHONE_RE.search(text):
        pii_types.append("phone")
        text = PHONE_RE.sub("[REDACTED_PHONE]", text)

    if SSN_RE.search(text):
        pii_types.append("ssn")
        text = SSN_RE.sub("[REDACTED_SSN]", text)

    return text, pii_types


def choose_route(prompt: str, expected_complexity: str | None) -> Literal["small", "standard", "premium"]:
    if expected_complexity == "high":
        return "premium"
    if expected_complexity == "medium":
        return "standard"
    if expected_complexity == "low":
        return "small"

    length = len(prompt)
    if length > 6000:
        return "premium"
    if length > 1200:
        return "standard"
    return "small"


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "llm-cost-compliance-gateway",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/v1/gateway", response_model=GatewayResponse)
def gateway(request: GatewayRequest) -> GatewayResponse:
    redacted, pii_types = redact_pii(request.prompt)
    route = choose_route(redacted, request.expected_complexity)

    return GatewayResponse(
        redacted_prompt=redacted,
        route=route,
        pii_types=pii_types,
        cache_status="not_checked",
        provider_called=False,
    )
