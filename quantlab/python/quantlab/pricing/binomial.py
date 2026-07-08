"""American option pricing: CRR binomial with discrete dividends, plus the
Black-Scholes closed form used as the mandatory European-limit check
(see inv-option-pricing-sde: no pricing number ships without its checks).

Reference implementation — clarity over speed. Whole-chain screens move to
the Rust core when they become hot paths.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


def black_scholes(spot: float, strike: float, t: float, r: float, vol: float,
                  right: str = "C", div_yield: float = 0.0) -> float:
    """European closed form (continuous dividend yield)."""
    if t <= 0:
        intrinsic = spot - strike if right == "C" else strike - spot
        return max(intrinsic, 0.0)
    d1 = (math.log(spot / strike) + (r - div_yield + vol * vol / 2) * t) / (vol * math.sqrt(t))
    d2 = d1 - vol * math.sqrt(t)
    n = lambda x: (1 + math.erf(x / math.sqrt(2))) / 2
    if right == "C":
        return spot * math.exp(-div_yield * t) * n(d1) - strike * math.exp(-r * t) * n(d2)
    return strike * math.exp(-r * t) * n(-d2) - spot * math.exp(-div_yield * t) * n(-d1)


@dataclass
class CRRPricer:
    """Cox-Ross-Rubinstein binomial tree, American exercise, discrete
    dividends via the escrowed-dividend method: the tree diffuses
    spot minus the PV of dividends paid before expiry; dividends are added
    back (at PV) when evaluating exercise before each ex-date.
    """

    steps: int = 800
    dividends: list[tuple[float, float]] = field(default_factory=list)  # (time_years, amount)

    def price(self, spot: float, strike: float, t: float, r: float, vol: float,
              right: str = "C", american: bool = True) -> float:
        if t <= 0:
            return max((spot - strike) if right == "C" else (strike - spot), 0.0)
        divs = [(td, d) for td, d in self.dividends if 0 < td < t]
        pv_divs = sum(d * math.exp(-r * td) for td, d in divs)
        s0 = spot - pv_divs
        if s0 <= 0:
            raise ValueError("PV of dividends exceeds spot")

        n = self.steps
        dt = t / n
        u = math.exp(vol * math.sqrt(dt))
        d = 1 / u
        disc = math.exp(-r * dt)
        p = (math.exp(r * dt) - d) / (u - d)
        if not 0 < p < 1:
            raise ValueError(f"no-arbitrage violated on grid: p={p:.4f}; reduce dt or check r/vol")

        sign = 1.0 if right == "C" else -1.0
        # Terminal payoffs (no remaining dividends at expiry).
        values = [
            max(sign * (s0 * u ** j * d ** (n - j) - strike), 0.0) for j in range(n + 1)
        ]
        for i in range(n - 1, -1, -1):
            t_i = i * dt
            # Dividends still ahead of node time re-enter the exercise value.
            escrow = sum(dv * math.exp(-r * (td - t_i)) for td, dv in divs if td > t_i)
            for j in range(i + 1):
                cont = disc * (p * values[j + 1] + (1 - p) * values[j])
                if american:
                    s_here = s0 * u ** j * d ** (i - j) + escrow
                    cont = max(cont, sign * (s_here - strike))
                values[j] = cont
        return values[0]

    def european_limit_check(self, spot: float, strike: float, t: float, r: float,
                             vol: float, right: str = "C", tol: float = 5e-3) -> float:
        """Mandatory verification: with no dividends and european exercise,
        the tree must converge to Black-Scholes. Returns |error|; raises
        beyond tolerance — a failing check invalidates the pricer, not the
        market."""
        if self.dividends:
            raise ValueError("run the check on a dividend-free configuration")
        tree = self.price(spot, strike, t, r, vol, right, american=False)
        closed = black_scholes(spot, strike, t, r, vol, right)
        err = abs(tree - closed)
        if err > tol:
            raise AssertionError(f"European limit check failed: |{tree:.5f}-{closed:.5f}|={err:.5f}>{tol}")
        return err
