"""quantlab: the data-science layer of the agentic-investing system.

Polars-first. Point-in-time rules from the inv-quant-foundations skill are
enforced in code here, not by convention: the lake refuses writes without
provenance, and benchmarks refuse construction without publication
timestamps.
"""

__all__ = ["lake", "benchmarks"]
