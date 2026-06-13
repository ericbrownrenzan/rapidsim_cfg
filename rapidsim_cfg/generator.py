"""
Top-level generator — connects DecayLine ↔ GlobalSettings ↔ ParticleBlocks
using the CORRECT RapidSim index ordering.
"""

from __future__ import annotations
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Union

from .decay import DecayLine
from .config import GlobalSettings, ParticleBlock, _sanitize_branch_name


class RapidSimProject:
    def __init__(
            self,
            decay: Optional[DecayLine] = None,
            global_settings: Optional[GlobalSettings] = None,
            particle_blocks: Optional[List[ParticleBlock]] = None,
            particle_table_path: Optional[str] = None,
            ):
        self.decay = decay
        self.global_settings = global_settings or GlobalSettings()
        self.particle_blocks: List[ParticleBlock] = list(particle_blocks or [])
        if particle_table_path is None:
            config_env = os.environ.get("RAPIDSIM_CONFIG")
            root_env = os.environ.get("RAPIDSIM_ROOT", "")
            if config_env:
                root = config_env
                # 蓝色文字提示用户自定义路径
                print(f"\033[94m[RapidSimProject] Using user-defined RAPIDSIM_CONFIG path: {root}\033[0m")
            else:
                root = root_env
                # 默认颜色提示默认路径
                print(f"[RapidSimProject] Using RapidSim default path (RAPIDSIM_ROOT): {root}")
            particle_table_path = os.path.join(root, "config", "particles.dat")
        if not os.path.exists(particle_table_path):
            raise FileNotFoundError(f"Particle table not found: {particle_table_path}")
        # 在 __init__ 中
        self._particle_names = set()          # 仅正粒子（第2列）
        self._anti_particle_names = set()     # 仅反粒子（第3列，排除 "---"）

        with open(particle_table_path, "r") as f:
            next(f)  # 跳过标题行
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = re.split(r'\s+', line)
                if len(parts) < 3:
                    continue
                name = parts[1].strip()
                anti = parts[2].strip()
                if name and name != "---":
                    self._particle_names.add(name)
                if anti and anti != "---":
                    self._anti_particle_names.add(anti)

        # 保留总集合用于校验（并集）
        self._valid_particle_names = self._particle_names | self._anti_particle_names
        print(f"[RapidSimProject] Loaded {len(self._valid_particle_names)} particle names from {particle_table_path}")

    # ── auto-build @0,@1,@2... blocks from decay ordering ────────────
    def autopopulate_particles(
        self,
        *,
        default_smear: Optional[str] = None,
        overrides: Optional[Dict[str, Dict]] = None,
    ) -> "RapidSimProject":
        overrides = overrides or {}
        table = self.decay.particle_index_table()

        self.particle_blocks = []
        
        for idx, role, pname, context in table:
            if pname not in self._valid_particle_names:
                raise ValueError(
                        f"Particle '{pname}' (index {idx}) is not defined in the loaded particle table. "
                        "Please check the decay file or provide a custom particle table via "
                        "the 'particle_table_path' argument when creating RapidSimProject."
                        )
            ov = overrides.get(pname, {})
            
            # 生成 user_name：粒子名 + 上下文 + @index（保证绝对唯一）
            if ov.get("user_name"):
                user_name = ov["user_name"]
            else:
                base = _sanitize_branch_name(pname)
                if context:
                    ctx = _sanitize_branch_name(context)
                    user_name = f"{base}_{ctx}_{idx}"
                else:
                    user_name = f"{base}_{idx}"
            
            self.particle_blocks.append(
                    ParticleBlock(
                        index=idx,
                        particle_name=pname,
                        context=context,
                        user_name=user_name,  # 现在绝对唯一
                        smear=ov.get("smear", default_smear),
                        invisible=ov.get("invisible", None),
                        altMass=ov.get("altMass", None),
                        evtGenModel=ov.get("evtGenModel", None),
                        extra=ov.get("extra", {}),
                        )
                    )
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

    # print particle tables
    def list_particles(self, include_anti: bool = True) -> None:
        """
        Print the loaded particle tables.

        Args:
            include_anti: include the anti-partile or not. the default is True
        """
        if not hasattr(self, '_particle_names') or not self._particle_names:
            print("[RapidSimProject] No particle table loaded.")
            return

        if include_anti:
            names = sorted(self._valid_particle_names)   # 直接使用已有的并集
            print(f"Loaded {len(names)} particle names:")
        else:
            names = sorted(self._particle_names)         # 仅正粒子
            print(f"Loaded {len(names)} particle names, anti-particles are not included:")

        for n in names:
            print(f"  {n}")

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
