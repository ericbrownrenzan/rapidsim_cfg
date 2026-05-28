"""
Renders the .config particle blocks in RapidSim's native expanded style:

@0
	name : Bs
@1
	name : Jpsi
	smear : LHCbGeneric
@2
	name : phi
	smear : LHCbGeneric
...

NOT the compact @# N Name style (which is also accepted but NOT what
RapidSim auto-generates when you first run it).
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Sequence, Union


def _sanitize_branch_name(s: str) -> str:
    """
    Roughly what RapidSim does to make a ROOT-safe branch label
    (you can override per-particle via explicit `name:` in overrides).
    """
    return (
        s.replace("+", "p")
         .replace("-", "m")
         .replace("~", "anti")
         .replace("#", "")
         .replace("*", "star")
    )


def _fmt(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "TRUE" if v else ""
    if isinstance(v, (list, tuple)):
        return " ".join(str(x) for x in v)
    return str(v)


def _kv(k: str, v: Any) -> str:
    if v is None:
        return f"{k} :"
    return f"{k} : {_fmt(v)}"


def _kv_omit_none(k: str, v: Any) -> Optional[str]:
    if v is None or v == "":
        return None
    return f"{k} : {_fmt(v)}"

# ────────────────────────────────────────────────────────────────────

class GlobalSettings:
    """
    Top-of-file global key:value block.

    Every recognised RapidSim global key is an explicit kwarg so IDEs
    can tab-complete; anything truly exotic goes into extra={}.
    """

    def __init__(
        self,
        *,
        seed: Any = 0,
        acceptance: str = "Any",       # Any|ParentIn|AllIn|AllDownstream
        geometry: str = "LHCb",         # 4pi|LHCb
        energy: Any = 13,               # 7|8|13|14
        parent: Any = None,             # b|c|None
        ptRange: Optional[Sequence[float]] = None,
        etaRange: Optional[Sequence[float]] = None,
        minWidth: float = 0.001,
        maxAttempts: int = 1000,
        paramsStable: Optional[Sequence[str]] = None,
        paramsDecaying: Optional[Sequence[str]] = None,
        paramsTwoBody: Optional[Sequence[str]] = None,
        paramsThreeBody: Optional[Sequence[str]] = None,
        useEvtGen: bool = False,
        evtGenUsePHOTOS: bool = False,
        pid: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        # raw trailing lines RapidSim also allows (param:/cut:/shape:)
        raw_lines: Optional[List[str]] = None,
    ):
        self.seed = seed
        self.acceptance = acceptance
        self.geometry = geometry
        self.energy = energy
        self.parent = parent
        self.ptRange = ptRange
        self.etaRange = etaRange
        self.minWidth = minWidth
        self.maxAttempts = maxAttempts
        self.paramsStable = paramsStable
        self.paramsDecaying = paramsDecaying
        self.paramsTwoBody = paramsTwoBody
        self.paramsThreeBody = paramsThreeBody
        self.useEvtGen = useEvtGen
        self.evtGenUsePHOTOS = evtGenUsePHOTOS
        self.pid = pid
        self.extra = dict(extra) if extra else {}
        self.raw_lines = list(raw_lines) if raw_lines else []

    def render(self) -> str:
        L = []
        L.append(_kv("seed", self.seed))
        L.append(_kv("acceptance", self.acceptance))
        L.append(_kv("geometry", self.geometry))
        L.append(_kv("energy", self.energy))
        if self.parent is not None and self.parent != "":
            L.append(f"parent : {_fmt(self.parent)}")
        if self.ptRange is not None:
            L.append(f"ptRange : {_fmt(self.ptRange)}")
        if self.etaRange is not None:
            L.append(f"etaRange : {_fmt(self.etaRange)}")
        L.append(_kv("minWidth", self.minWidth))
        L.append(_kv("maxAttempts", self.maxAttempts))
        if self.paramsStable is not None:
            L.append(_kv("paramsStable", self.paramsStable))
        if self.paramsDecaying is not None:
            L.append(_kv("paramsDecaying", self.paramsDecaying))
        if self.paramsTwoBody is not None:
            L.append(_kv("paramsTwoBody", self.paramsTwoBody))
        if self.paramsThreeBody is not None:
            L.append(_kv("paramsThreeBody", self.paramsThreeBody))
        if self.useEvtGen:
            L.append("useEvtGen : TRUE")
        if self.evtGenUsePHOTOS and self.useEvtGen:
            L.append("evtGenUsePHOTOS : TRUE")
        if self.pid:
            L.append(_kv("pid", self.pid))
        for k, v in self.extra.items():
            L.append(_kv(k, v))
        for rl in self.raw_lines:
            L.append(rl)
        return "\n".join(L)


# ────────────────────────────────────────────────────────────────────

class ParticleBlock:
    """
    One @N block in the .config file.

    `particle_name` is the particles.dat lookup key (mu+, Bs0, Jpsi …).
    `user_name` is the optional `name :` (branch-label).  When None,
    the generator will derive one via _sanitize_branch_name().
    """

    def __init__(
        self,
        *,
        index: int,
        particle_name: str,
        user_name: Optional[str] = None,
        smear: Optional[Union[str, List[str]]] = None,
        invisible: Optional[bool] = None,
        altMass: Optional[Sequence[str]] = None,
        evtGenModel: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ):
        self.index = index
        self.particle_name = particle_name
        self.user_name = user_name
        self.smear = smear
        self.invisible = invisible
        self.altMass = altMass
        self.evtGenModel = evtGenModel
        self.extra = dict(extra) if extra else {}

    def render(self) -> str:
        lines = [f"@{self.index}"]
        # If caller never set user_name, derive from particle_name
        nm = self.user_name if self.user_name is not None else _sanitize_branch_name(self.particle_name)
        lines.append(f"\tname : {nm}")
        if self.smear:
            if isinstance(self.smear, (list, tuple)):
                for s in self.smear:
                    lines.append(f"\tsmear : {s}")
            else:
                lines.append(f"\tsmear : {self.smear}")
        if self.invisible is not None:
            lines.append(f"\tinvisible : {'TRUE' if self.invisible else ''}")
        if self.altMass:
            lines.append(f"\taltMass : {' '.join(self.altMass)}")
        if self.evtGenModel:
            lines.append(f"\tevtGenModel : {self.evtGenModel}")
        for k, v in self.extra.items():
            lines.append(f"\t{k} : {_fmt(v)}")
        return "\n".join(lines)
