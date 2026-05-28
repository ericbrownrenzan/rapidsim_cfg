"""
Models a RapidSim .decay line and CANONICALLY determines particle ordering.

RapidSim's own parser reads the decay line left→right and numbers particles by:

  Pass 1:  @0 = mother
  Pass 2:  @1,@2,... = each {intermediate -> ...} block's head particle,
           in left→right order of the {} blocks
  Pass 3:  @N+1,@N+2,... = leaf (final-state) particles,
           iterating blocks left→right, and within each block left→right

This module reproduces exactly that ordering so the .config @0,@1,@2...
blocks come out in the same sequence RapidSim would assign.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple


# ────────────────────────────────────────────────────────────────────
# Core data structure
# ────────────────────────────────────────────────────────────────────

@dataclass
class DecayBlock:
    """
    One { X -> a b ... } sub-decay block.

    Attributes
    ----------
    intermediate : str
        The resonant/intermediate particle NAME AS IT APPEARS IN THE BLOCK HEAD
        (e.g. "Jpsi", "phi", "D0").
    finals : List[str]
        Final-state particle names (e.g. ["mu+","mu-"] or ["K+","K-"]).
        MUST be length ≥ 1.  These are *not* further expanded — they are
        leaf particles that must exist in particles.dat.
    """
    intermediate: str
    finals: List[str]

    def __post_init__(self):
        if not self.finals:
            raise ValueError(
                f"DecayBlock for '{self.intermediate}' has no final states; "
                f"write at least one leaf particle."
            )


@dataclass
class DecayLine:
    """
    Represents ONE decay-line:

        mother -> {X1 -> a b} {X2 -> c d} ...

    The *order of blocks matters*: it determines @-index assignment.
    """
    mother: str
    blocks: List[DecayBlock] = field(default_factory=list)

    # ── canonical index assignment ─────────────────────────────────

    def particle_index_table(self) -> List[Tuple[int, str, str]]:
        """
        Return [(index, role, particle_name), ...] in RapidSim-canonical order.

        role ∈ {"mother", "intermediate", "final"}
        """
        table: List[Tuple[int, str, str]] = []

        # Pass 1
        table.append((0, "mother", self.mother))

        # Pass 2 – intermediates (left→right blocks)
        for blk in self.blocks:
            table.append((len(table), "intermediate", blk.intermediate))

        # Pass 3 – finals (blocks left→right, within-block left→right)
        for blk in self.blocks:
            for f in blk.finals:
                table.append((len(table), "final", f))

        return table

    def particle_index_map(self) -> dict:
        """{particle_name: index} — last occurrence wins if duplicated."""
        return {name: idx for idx, _, name in self.particle_index_table()}

    # ── render .decay line ──────────────────────────────────────────

    def render(self) -> str:
        inner = " ".join(
            f"{{ {blk.intermediate} -> {' '.join(blk.finals)} }}"
            for blk in self.blocks
        )
        return f"{self.mother} -> {inner}"

    # ── convenience constructors ───────────────────────────────────

    @classmethod
    def build(cls, mother: str, **block_spec) -> "DecayLine":
        """
        DecayLine.build("Bs0", Jpsi=["mu+","mu-"], phi=["K+","K-"])
        """
        blocks = []
        for inter, fins in block_spec.items():
            if not isinstance(fins, (list, tuple)):
                fins = [fins]
            blocks.append(DecayBlock(intermediate=inter, finals=list(fins)))
        return cls(mother=mother, blocks=blocks)

    @classmethod
    def from_dict(cls, d: dict) -> "DecayLine":
        """
        {
            "mother": "Bs0",
            "branches": {"Jpsi": ["mu+","mu-"], "phi": ["K+","K-"]}
        }
        """
        mother = d["mother"]
        branches = d["branches"]
        blocks = [
            DecayBlock(intermediate=k, finals=v if isinstance(v, list) else [v])
            for k, v in branches.items()
        ]
        return cls(mother=mother, blocks=blocks)