from rapidsim_cfg import (
    RapidSimProject,
	build_cascade_decay,
    DecayLine,
    DecayBlock,
    GlobalSettings,
)

from rapidsim_cfg import DecayLine, DecayBlock

# Lambda0 -> p+ pi-   (treated as leaf here; if Lambda0 itself decays, wrap similarly)
lambda0_leaf = "Lambda0"   # leaf string

# Lambdac+ -> { Lambda0 -> p+ pi- } pi+
lambdac = DecayBlock(
    intermediate="Lambdac+",
    finals=[
        DecayBlock("Lambda0", ["p+", "pi-"]),  # nested decay
        "pi+",                                  # bare sibling
    ],
)

# Sigmac++ -> { Lambdac+ -> { Lambda0 -> p+ pi- } pi+ } pi+
sigmac = DecayBlock(
    intermediate="Sigmac++",
    finals=[
        lambdac,
        "pi+",   # <-- bare pi+ *alongside* the nested Lambdac+
    ],
)

decay = DecayLine(
    mother="Lambdab0",
    blocks=[
        sigmac,
        DecayBlock("D-",   ["K+", "pi-", "pi-"]),
        DecayBlock("pi0",  ["gamma", "gamma"]),
    ],
    direct_finals=["K-"],
)

print(decay.render())

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
        #"Lambdab0": {"user_name":"myLb"},
        #"Sigmacc++": {},
        #"Lambdac+": {},
        #"Lambdab0": {},
        #"pi+" : {},
        "D-" : {},
        #"K-": {"user_name": "bachelar_K", "smear": "LHCbGenericIP"},
        #"pi0": {"user_name": "mypi0"}
    },
)

proj.write("Lb2SigmacDKpi0")

