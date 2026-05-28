from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict


@dataclass
class DecayBlock:
    """One { intermediate -> f1 f2 ... }"""
    intermediate: str
    finals: List[str]

    def __post_init__(self):
        if not self.finals:
            raise ValueError(
                f"DecayBlock('{self.intermediate}'): finals must be non-empty"
            )


class DecayLine:
    """
    Represent ONE decay line with canonical RapidSim numbering.
    
    Example:
        B+ -> { Jpsi -> mu+ mu- } { phi -> K+ K- } K+
    """

    def __init__(
        self,
        mother: str,
        blocks: Optional[List[DecayBlock]] = None,
        direct_finals: Optional[List[str]] = None,
    ):
        self.mother = mother
        self.blocks: List[DecayBlock] = list(blocks or [])
        self.direct_finals: List[str] = list(direct_finals or [])

    def particle_index_table(self) -> List[Tuple[int, str, str, Optional[str]]]:
        """
        Returns [(index, role, particle_name, context), ...]
        
        role ∈ {"mother","intermediate","direct_final","daughter"}
        context = None or intermediate name (for daughters)
        """
        table: List[Tuple[int, str, str, Optional[str]]] = []

        # @0: mother
        table.append((0, "mother", self.mother, None))

        # @1..@Ninter: {} block heads
        for blk in self.blocks:
            table.append((len(table), "intermediate", blk.intermediate, None))

        # direct finals
        for p in self.direct_finals:
            table.append((len(table), "direct_final", p, None))

        # daughters of each {} block
        for blk in self.blocks:
            for d in blk.finals:
                table.append((len(table), "daughter", d, blk.intermediate))

        return table

    def render(self) -> str:
        blocks_str = " ".join(
            f"{{ {blk.intermediate} -> {' '.join(blk.finals)} }}"
            for blk in self.blocks
        )
        parts = [f"{self.mother} ->", blocks_str]
        if self.direct_finals:
            parts.append(" ".join(self.direct_finals))
        return " ".join(parts)

    @classmethod
    def build(
        cls,
        mother: str,
        /,
        *,
        intermediates: Optional[Dict[str, List[str]]] = None,
        direct_finals: Optional[List[str]] = None,
        **kw_intermediates,
    ) -> "DecayLine":
        if intermediates is not None:
            blocks = [
                DecayBlock(k, list(v))
                for k, v in intermediates.items()
            ]
            return cls(mother=mother, blocks=blocks, direct_finals=direct_finals)

        if kw_intermediates:
            blocks = [
                DecayBlock(k, list(v))
                for k, v in kw_intermediates.items()
            ]
            return cls(mother=mother, blocks=blocks)

        return cls(mother=mother)