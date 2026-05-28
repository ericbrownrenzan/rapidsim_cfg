"""
Top-level generator — connects DecayLine ↔ GlobalSettings ↔ ParticleBlocks
using the CORRECT RapidSim index ordering.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from .decay import DecayLine
from .config import GlobalSettings, ParticleBlock


class RapidSimProject:
    def __init__(
        self,
        decay: DecayLine,
        global_settings: Optional[GlobalSettings] = None,
        particle_blocks: Optional[List[ParticleBlock]] = None,
    ):
        self.decay = decay
        self.global_settings = global_settings or GlobalSettings()
        self.particle_blocks: List[ParticleBlock] = list(particle_blocks or [])

    # ── auto-build @0,@1,@2... blocks from decay ordering ────────────

    def autopopulate_particles(
        self,
        *,
        default_smear: Optional[str] = None,
        overrides: Optional[Dict[str, Dict]] = None,
    ) -> "RapidSimProject":
        """
        Fill self.particle_blocks from the decay line's canonical index table.

        overrides = {
            "mu+": {"smear": "LHCbGeneric", "user_name": "mup"},
            "Jpsi": {"smear": "LHCbGeneric"},
            ...
        }
        Keys match particle_name (the particles.dat lookup key), NOT user_name.
        """
        overrides = overrides or {}
        table = self.decay.particle_index_table()

        self.particle_blocks = []
        for idx, role, pname in table:
            ov = overrides.get(pname, {})
            pb = ParticleBlock(
                index=idx,
                particle_name=pname,
                user_name=ov.get("user_name", None),
                smear=ov.get("smear", default_smear),
                invisible=ov.get("invisible", None),
                altMass=ov.get("altMass", None),
                evtGenModel=ov.get("evtGenModel", None),
                extra=ov.get("extra", {}),
            )
            self.particle_blocks.append(pb)

        return self

    # ── rendering ────────────────────────────────────────────────────

    def render_decay(self) -> str:
        return self.decay.render()

    def render_config(self) -> str:
        parts = [self.global_settings.render(), ""]
        for pb in self.particle_blocks:
            parts.append(pb.render())
            parts.append("")  # blank line between blocks
        return "\n".join(parts)

    # ── writing ─────────────────────────────────────────────────────

    def write(
        self,
        out_dir: Union[str, os.PathLike],
        prefix: Optional[str] = None,
    ):
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        p = prefix or self.decay.mother

        decay_path = out / f"{p}.decay"
        config_path = out / f"{p}.config"

        decay_path.write_text(self.render_decay() + "\n", encoding="utf-8")
        config_path.write_text(self.render_config(), encoding="utf-8")

        print(f"[RapidSimCfg] written:\n  {decay_path}\n  {config_path}")

    # ── factory from plain dict (YAML/JSON-friendly) ────────────────

    @classmethod
    def from_dict(cls, d: Dict) -> "RapidSimProject":
        decay = DecayLine.from_dict(d)

        gs_kwargs = {k: v for k, v in d.get("global", {}).items()}
        gs = GlobalSettings(**gs_kwargs)

        proj = cls(decay=decay, global_settings=gs)
        proj.autopopulate_particles(
            default_smear=d.get("_default_smear", None),
            overrides=d.get("particles", {}),
        )
        return proj