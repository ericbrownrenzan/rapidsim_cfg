# RapidSim Config Generator

A small Python package to **generate valid RapidSim `.decay` and `.config` files** directly from Python objects or dictionaries.

Correct particle numbering  
Correct `{ X -> a b }` decay syntax  
Compatible with RapidSim's official `validation/` outputs  

---

## Installation
```bash
git clone https://github.com/your-org/rapidsim-cfg.git
cd rapidsim-cfg
pip install -e .
```

## Quick Start
```python
from rapidsim_cfg import (
    RapidSimProject,
    DecayLine,
    DecayBlock,
    GlobalSettings,
)

decay = DecayLine(
    mother="B+",
    blocks=[
        DecayBlock("Jpsi", ["mu+", "mu-"]),
        DecayBlock("phi", ["K+", "K-"]),
    ],
    direct_finals=["K+","pi0"],
)

gs = GlobalSettings(
    seed=12345,
    acceptance="LHCb",
    geometry="LHCb",
    energy=13,
    maxAttempts=10000,
    paramsStable=["P", "PT", "ETA", "PHI"],
    paramsDecaying=["M", "P", "PT", "ETA", "PHI"],
)

proj = RapidSimProject(decay=decay, global_settings=gs)

proj.autopopulate_particles(
    default_smear="LHCbGeneric",
    overrides={
        "B+": {"user_name":"myBplus"},
        "Jpsi": {},
        "phi": {},
        "mu+": {},
        "mu-": {},
        "K-": {},
        "pi0": {"user_name": "mypi0"}
    },
)

proj.write("Bplus2JpsiphiKpi0")
```
## Why This Package Exists
RapidSim config files are:
- Order-sensitive
- Whitespace-sensitive
- Hard to edit by hand safely
This package guarantees:
- Correct particle numbering
- Correct decay syntax
- Minimal, clean .configoutput
- Reproducible generation from code or data
