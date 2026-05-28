from rapidsim_cfg import (
    RapidSimProject,
	build_cascade_decay,
    DecayLine,
    DecayBlock,
    GlobalSettings,
)

decay = build_cascade_decay(
    "Lambdab0",
    cascade={
        "Sigmac++": {
            "Lambdac+": {
                "Lambda0": ["p+", "pi-"],
                "pi+" : []},
            "pi+": [],
            },
        "D-" : ["K-", "pi+", "pi-"], 
        "pi0" : ["gamma", "gamma"],
    },
    direct_finals=["K-"],
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
        "Lambdab0": {"user_name":"myLb"},
        "K-": {"user_name":"bachelar_K", "smear": ["LHCbGenericIP", "LHCbGeneric"]},
        "pi0": {"user_name": "mypi0"}
    },
)

proj.write("Lb2SigmacDKpi0")

