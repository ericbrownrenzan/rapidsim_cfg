from rapidsim_cfg import (
    RapidSimProject,
	build_cascade_decay,
    DecayLine,
    DecayBlock,
    GlobalSettings,
)

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
    acceptance="AllIn",
    geometry="LHCb",
    energy=13,
    maxAttempts=10000,
    paramsStable=["P", "PT", "PX", "PY", "PZ", "E", "M", "eta", "phi", "ProbNNp", "ProbNNk", "ProbNNpi", "IP", "y"],
    paramsDecaying=["M", "P", "PT", "eta", "phi", "vtxX", "vtxY", "vtxZ", "IP", "MINIP", "SIGMAIP", "SIGMAMINIP", "FD", "y", "PX", "PY", "PZ", "E"],
    useEvtGen=True,
    evtGenUsePHOTOS=True,
    extra = { "param" : "mKpi_Dm M 7 8"}
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
        "D-" : {"evtGenModel": "D_DALITZ"},
        "K-": { "smear": [ "LHCbGenericIP", "LHCbGeneric"]},
        "p+": { "smear": [ "LHCbGenericIP", "LHCbGeneric"]},
        "pi+": { "smear": [ "LHCbGenericIP", "LHCbGeneric"]},
        "pi-": { "smear": [ "LHCbGenericIP", "LHCbGeneric"]},
        #"pi0": {"user_name": "mypi0"}
    },
)

proj.write("Lb2SigmacDKpi0")

