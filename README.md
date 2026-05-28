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
See `demo.py`
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
