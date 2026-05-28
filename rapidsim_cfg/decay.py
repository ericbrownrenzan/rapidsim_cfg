from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Union, Dict


# ────────────────────────────────────────────────────────────────────
@dataclass
class DecayBlock:
    """
    Represents one { intermediate -> ... } block.
    
    finals can be:
      - str: final-state particle name
      - DecayBlock: another nested decay block
    """
    intermediate: str
    finals: List[Union[str, "DecayBlock"]]

    def __post_init__(self):
        pass


# ────────────────────────────────────────────────────────────────────
class DecayLine:
    """
    Represent ONE decay line with nested {} blocks.
    
    Example:
        B+ -> { Psi(2S) -> { Jpsi -> mu+ mu- } gamma } { phi -> K+ K- } K+
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
    """
    def _collect_particles(
        self,
        order: List[Tuple[int, str, str, Optional[str]]],
        block: DecayBlock,
        parent_context: Optional[str] = None,
    ):
        #Recursively collect particles from a DecayBlock.
        # Add intermediate particle
        order.append((len(order), "intermediate", block.intermediate, parent_context))
        
        # Process finals
        for final in block.finals:
            if isinstance(final, DecayBlock):
                # Nested block: recurse with current intermediate as context
                self._collect_particles(order, final, block.intermediate)
            else:
                # Final-state particle
                order.append((len(order), "daughter", final, block.intermediate))
    """
    def _collect_particles(
            self,
            order: List[Tuple[int, str, str, Optional[str]]],
            block: DecayBlock,
            parent_context: Optional[str] = None,
            ):
    # 添加中间粒子
        order.append((len(order), "intermediate", block.intermediate, parent_context))

        # 处理衰变产物
        for final in block.finals:
            if isinstance(final, DecayBlock):
                # 嵌套衰变
                self._collect_particles(order, final, block.intermediate)
            else:
                # ✅ 字符串 = 直接末态粒子
                order.append((len(order), "daughter", final, block.intermediate))
    def particle_index_table(self) -> List[Tuple[int, str, str, Optional[str]]]:
        """
        RapidSim 的真实扫描顺序（严格对齐用户验证结果）：

        B+ -> { Psi(2S) -> { Jpsi -> mu+ mu- } gamma } { phi -> K+ K- } K+

        @0 B+
        @1 Psi(2S)
        @2 phi
        @3 K+ (direct)
        @4 Jpsi
        @5 gamma
        @6 K+ (from phi)
        @7 K- (from phi)
        @8 mu+
        @9 mu-
        """
        order: List[Tuple[int, str, str, Optional[str]]] = []

        # 1. mother
        order.append((0, "mother", self.mother, None))

        # 2. top blocks
        top_blocks = []
        for blk in self.blocks:
            top_blocks.append(blk)
            order.append((len(order), "intermediate", blk.intermediate, None))

        # 3. direct_finals
        for p in self.direct_finals:
            order.append((len(order), "direct_final", p, None))

        nested_blocks = []  # 收集嵌套块，以便后续处理
        for blk in top_blocks:
            # 收集该块的内部块头（嵌套块）
            for final in blk.finals:
                if isinstance(final, DecayBlock):
                    nested_blocks.append(final)
                    order.append((len(order), "intermediate", final.intermediate, blk.intermediate))
            # 收集该块的非块末态
            for final in blk.finals:
                if not isinstance(final, DecayBlock):
                    order.append((len(order), "daughter", final, blk.intermediate))

        def process_nested(block: DecayBlock, parent_ctx: str):
            for final in block.finals:
                if not isinstance(final, DecayBlock):
                    order.append((len(order), "daughter", final, parent_ctx))
                else:
                    process_nested(final, final.intermediate)

        for nb in nested_blocks:
            process_nested(nb, nb.intermediate)

        return order
    def render(self) -> str:
        """Render the complete decay line."""
        def render_block(block: DecayBlock) -> str:
            inner_parts = []
            for final in block.finals:
                if isinstance(final, DecayBlock):
                    inner_parts.append(render_block(final))
                else:
                    inner_parts.append(final)
            
            inner = " ".join(inner_parts)
            return f"{{ {block.intermediate} -> {inner} }}"
        
        blocks_str = " ".join(render_block(b) for b in self.blocks)
        parts = [f"{self.mother} ->", blocks_str]
        
        if self.direct_finals:
            parts.append(" ".join(self.direct_finals))
        
        return " ".join(parts)

    @classmethod
    def build_nested(
        cls,
        mother: str,
        /,
        *,
        intermediates: Optional[Dict[str, Union[List[str], Dict]]] = None,
        direct_finals: Optional[List[str]] = None,
    ) -> "DecayLine":
        """
        Build a decay line with nested structures.
        
        Example:
            DecayLine.build_nested(
                "B+",
                intermediates={
                    "Psi(2S)": {
                        "Jpsi": ["mu+", "mu-"],
                        "gamma": []
                    },
                    "phi": ["K+", "K-"]
                },
                direct_finals=["K+"]
            )
        """

        """
        def build_block(key: str, value: Union[List[str], Dict]) -> DecayBlock:
            if isinstance(value, dict):
                # Nested: key -> {subkey -> ...}
                finals = []
                for sub_key, sub_val in value.items():
                    if isinstance(sub_val, list):
                        finals.append(DecayBlock(sub_key, sub_val))
                    else:
                        finals.append(DecayBlock(sub_key, [sub_val]))
                return DecayBlock(key, finals)
            else:
                # Simple: key -> [final1, final2, ...]
                return DecayBlock(key, value)
        """
        def build_block(key: str, value: Union[List[str], Dict]) -> DecayBlock:
            if isinstance(value, dict):
                finals = []
                for sub_key, sub_val in value.items():
                    if isinstance(sub_val, list):
                        if sub_val:  # ✅ 非空列表 → 继续衰变
                            finals.append(DecayBlock(sub_key, sub_val))
                        else:       # ✅ 空列表 → 不继续衰变，直接作为字符串
                            finals.append(sub_key)
                    else:
                        finals.append(DecayBlock(sub_key, [sub_val]))
                return DecayBlock(key, finals)
            else:
                return DecayBlock(key, value)

        
        blocks = []
        if intermediates:
            for key, val in intermediates.items():
                blocks.append(build_block(key, val))
        
        return cls(mother=mother, blocks=blocks, direct_finals=direct_finals)


# ────────────────────────────────────────────────────────────────────
# Convenience functions for common patterns
# ────────────────────────────────────────────────────────────────────

def build_cascade_decay(
    mother: str,
    cascade: Dict[str, Union[str, List[str], Dict]],
    direct_finals: Optional[List[str]] = None,
) -> DecayLine:
    """
    Build a cascade decay like:
        B+ -> { Psi(2S) -> { Jpsi -> mu+ mu- } gamma } { phi -> K+ K- } K+
    
    Args:
        mother: Mother particle name
        cascade: Nested dictionary describing the decay chain
        direct_finals: Particles that appear directly after all {} blocks
    
    Example:
        build_cascade_decay(
            "B+",
            {
                "Psi(2S)": {
                    "Jpsi": ["mu+", "mu-"],
                    "gamma": []
                },
                "phi": ["K+", "K-"]
            },
            direct_finals=["K+"]
        )
    """
    return DecayLine.build_nested(
        mother,
        intermediates=cascade,
        direct_finals=direct_finals,
    )
