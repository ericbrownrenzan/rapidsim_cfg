from rapidsim_cfg import (
    RapidSimProject,
	build_cascade_decay,
    DecayLine,
    DecayBlock,
    GlobalSettings,
)

decay = build_cascade_decay(
    "B+",
    cascade={
        "psi2S": {
            "Jpsi": ["mu+", "mu-"],
            "gamma": [],
        },
        #"pi0" : ["gamma", "gamma"],
        "phi": ["K+", "K-"],
    },
    direct_finals=["K+"],
)

gs = GlobalSettings(
    seed=12345,
    geometry="LHCb",
    energy=13,
    paramsStable=["P", "PT", "PX", "PY", "PZ"],
    paramsDecaying=["M", "P", "PT", "eta", "phi", "y"],
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
        "K-": {"smear": "LHCbGenericIP"},
        #"pi0": {"user_name": "mypi0"}
    },
)

proj.write("Bplus2Psi2sphiK")
