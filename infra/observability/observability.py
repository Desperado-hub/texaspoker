"""Monitoring and observability scaffolding."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Dict, List, Optional


@dataclass
class Metric:
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time)


@dataclass
class TraceSpan:
    name: str
    start: float = field(default_factory=time)
    end: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)

    def finish(self) -> None:
        self.end = time()

    @property
    def duration_ms(self) -> Optional[float]:
        if self.end is None:
            return None
        return (self.end - self.start) * 1000


class ObservabilityToolkit:
    """Collects metrics, traces, and audit events for poker services."""

    def __init__(self) -> None:
        self.metrics: List[Metric] = []
        self.traces: List[TraceSpan] = []
        self.audit_logs: List[str] = []
        self.slo_targets: Dict[str, float] = {"p99_latency_ms": 200.0, "error_rate": 0.01}

    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        self.metrics.append(Metric(name=name, value=value, labels=labels or {}))

    def start_trace(self, name: str, tags: Optional[Dict[str, str]] = None) -> TraceSpan:
        span = TraceSpan(name=name, tags=tags or {})
        self.traces.append(span)
        return span

    def log_audit(self, message: str) -> None:
        self.audit_logs.append(message)

    def slo_breaches(self) -> List[str]:
        """Return human-readable SLO breaches based on collected metrics."""
        breaches: List[str] = []
        latency_samples = [m.value for m in self.metrics if m.name == "latency_ms"]
        if latency_samples:
            p99 = sorted(latency_samples)[int(len(latency_samples) * 0.99) - 1]
            if p99 > self.slo_targets["p99_latency_ms"]:
                breaches.append(f"p99 latency {p99:.2f}ms exceeds target {self.slo_targets['p99_latency_ms']}ms")
        error_samples = [m.value for m in self.metrics if m.name == "error_rate"]
        if error_samples and max(error_samples) > self.slo_targets["error_rate"]:
            breaches.append("error rate exceeds target")
        return breaches
