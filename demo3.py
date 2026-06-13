from rapidsim_cfg import (
    RapidSimProject,
	build_cascade_decay,
    DecayLine,
    DecayBlock,
    GlobalSettings,
)

decay = build_cascade_decay(
    "B0",
    cascade={
        "Lambdac+": ["p+", "K-", "pi+"],
        "Lambdac-": ["p-", "K+", "pi-"],
        "pi0" : ["gamma", "gamma"]
    },
)

gs = GlobalSettings(
    seed=12345,
    geometry="LHCb",
    energy=13,
    #paramsStable=["P", "PT", "PX", "PY", "PZ"],
    paramsStable=["P", "PT", "PX", "PY", "PZ", "E", "M", "eta", "phi", "ProbNNp", "ProbNNk", "ProbNNpi", "IP", "y"],
    paramsDecaying=["M", "P", "PT", "eta", "phi", "y"],
    useEvtGen=True,
    evtGenUsePHOTOS=True,
    extra = { "param" : "mLcLc M 1 2"}
)

#proj = RapidSimProject(decay=decay, global_settings=gs)
proj = RapidSimProject()
proj.decay=decay
proj.global_settings=gs
proj.list_particles()          # 打印所有粒子名（含反粒子）
proj.list_particles(include_anti=False)  # 仅打印粒子名（不含反粒子）

proj.autopopulate_particles(
    default_smear="LHCbGeneric",
    overrides={
        "B0": {"user_name":"myBd"},
        "K-": { "smear": [ "LHCbGenericIP", "LHCbGeneric"]},
        "K+": { "smear": [ "LHCbGenericIP", "LHCbGeneric"]},
        "p+": { "smear": [ "LHCbGenericIP", "LHCbGeneric"]},
        "p-": { "smear": [ "LHCbGenericIP", "LHCbGeneric"]},
        "pi+": { "smear": [ "LHCbGenericIP", "LHCbGeneric"]},
        "pi-": { "smear": [ "LHCbGenericIP", "LHCbGeneric"]},
        "pi0": {"user_name": "mypi0"}
    },
)

proj.write("Bd2LcLcpi0")
