ALLOWLISTED_SERVER_IDS = [
    759881688506957844,
    664571288463081481
]

SUBJECT_ID_TRANSLATOR = {
    "CSCI": "a38d54eb-559d-4d6a-9a28-edfc1a4e67d5",
    "PSYO": "15f332e2-1f8a-428d-ab4e-41d06e9435fe",
    "MATH": "02074a28-392e-48e8-8ed3-417205cd1915",
    "STAT": "f49f0a99-2481-4a1d-95ad-095bd7d6e72c",
    "BUSS": "2dfdb588-0589-45d1-8dbb-0b5bc3b8e523",
    "ECON": "078792e2-b807-45f1-b923-35608d8f6df5",
    "MGMT": "f5f6e5ff-cd3e-48a1-81f7-e4fc11460672"
}

SCHOOL_ID_TRANSLATOR = {
    "Dalhousie University": "18345bee-1ad5-45cf-bd7e-61d660845f8f"
}


SUBJECT_ID_REVERSE_TRANSLATOR = {v: k for k, v in SUBJECT_ID_TRANSLATOR.items()}
SCHOOL_ID_REVERSE_TRANSLATOR = {v: k for k, v in SCHOOL_ID_TRANSLATOR.items()}

DALHOUSIE_SUBJECT_LISTS = [
    "ASSC",
    "BIOL",
    "CSCI",
    "ECON",
    "ENGL",
    "MATH",
    "MGMT",
    "PSYO",
    "STAT"
]