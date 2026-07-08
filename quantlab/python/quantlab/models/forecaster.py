"""Forecaster interface: baselines and foundation models behind one door.

Doctrine (inv-foundation-models skill): every model — seasonal-naive,
GBM, Chronos, TimesFM — implements the same interface and is evaluated on
the same Benchmark with identical splits. An FM that doesn't beat
seasonal-naive on a series gets benched for that series, in writing.

Foundation-model wrappers import lazily and fail loudly with install
hints, so the core package has no heavy dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


class Forecaster(Protocol):
    name: str

    def forecast(self, history: Sequence[float], horizon: int) -> list[float]:
        """Point forecast for the next `horizon` steps given trailing history."""
        ...


@dataclass
class NaiveDrift:
    """Last value + mean drift. The floor every model must beat."""

    name: str = "naive_drift"

    def forecast(self, history: Sequence[float], horizon: int) -> list[float]:
        if len(history) < 2:
            return [history[-1]] * horizon
        drift = (history[-1] - history[0]) / (len(history) - 1)
        return [history[-1] + drift * (i + 1) for i in range(horizon)]


@dataclass
class SeasonalNaive:
    """Value from one season ago (season=4 for quarterly fundamentals)."""

    season: int = 4
    name: str = "seasonal_naive"

    def forecast(self, history: Sequence[float], horizon: int) -> list[float]:
        if len(history) < self.season:
            return [history[-1]] * horizon
        return [history[-self.season + (i % self.season)] for i in range(horizon)]


@dataclass
class ChronosForecaster:
    """Amazon Chronos(-Bolt) zero-shot wrapper. Optional dependency.

    Median of sampled paths as the point forecast; use `.quantiles()` in
    analysis code when intervals matter (they usually do).
    """

    model_id: str = "amazon/chronos-bolt-small"
    name: str = "chronos"

    def forecast(self, history: Sequence[float], horizon: int) -> list[float]:
        try:
            from chronos import BaseChronosPipeline  # type: ignore
        except ImportError as e:  # pragma: no cover - env-dependent
            raise ImportError(
                "Chronos not installed: pip install chronos-forecasting torch "
                "(CPU is fine for -bolt-small; verify current checkpoint per "
                "the inv-foundation-models skill before relying on it)"
            ) from e
        import torch  # type: ignore

        pipeline = BaseChronosPipeline.from_pretrained(self.model_id, device_map="cpu")
        context = torch.tensor(list(history), dtype=torch.float32)
        quantiles, _ = pipeline.predict_quantiles(
            context=context, prediction_length=horizon, quantile_levels=[0.5]
        )
        return quantiles[0, :, 0].tolist()


def bench_table(results: list[dict]) -> str:
    """Render evaluate() outputs for several models into one comparison
    table (markdown) — the artifact that decides which model earns the
    series. Results must share a benchmark fingerprint or this raises."""
    fps = {r["fingerprint"] for r in results}
    if len(fps) != 1:
        raise ValueError(f"results span different benchmarks: {fps}")
    lines = [
        f"Benchmark `{results[0]['benchmark']}` (fingerprint {fps.pop()})",
        "",
        "| model | MAE | MAPE | dir hit | n |",
        "|---|---|---|---|---|",
    ]
    for r in sorted(results, key=lambda r: r["pooled"]["mae"]):
        p = r["pooled"]
        mape = "—" if p["mape"] is None else f"{p['mape']:.3f}"
        lines.append(
            f"| {r['model']} | {p['mae']:.4g} | {mape} | {p['dir_hit']:.2%} | {p['n']} |"
        )
    return "\n".join(lines)
