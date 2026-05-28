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
```
from rapidsim_cfg import RapidSimProject, DecayLine, GlobalSettings

decay = DecayLine.build(
    "Bs0",
    Jpsi=["mu+", "mu-"],
    phi=["K+", "K-"],
)

gs = GlobalSettings(
    seed=42,
    acceptance="AllIn",
    geometry="LHCb",
    energy=13,
    ptRange=[2, 30],
    maxAttempts=10000,
    paramsStable=["P", "PT", "ETA", "PHI"],
    paramsDecaying=["M", "P", "PT", "ETA", "PHI"],
)

proj = RapidSimProject(decay=decay, global_settings=gs)
proj.autopopulate_particles(
    default_smear="LHCbGeneric",
    overrides={
        "mu+": {},
        "mu-": {},
        "K+": {},
        "K-": {},
        "Jpsi": {},
        "phi": {},
    },
)

proj.write("Bs2Jpsiphi")
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
