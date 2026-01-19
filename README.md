# Unit-level-Turnover-Model
The repository contains the code for the data-driven complement to energy-emissions model developed in the paper "The race between renewable electricity and demand governs the future of fossil power".

The model explicitly resolves unit-level fossil power plant dynamics to assess how alternative trajectories of renewable generation and electricity demand growth shape fossil capacity evolution, CCUS deployment, future emissions, and system costs.

The codebase is organized into the following modules:

0_SetAndRun: Defines the core model settings, including the simulation period, and constructs a structured sensitivity grid spanning a broad range of renewable generation and electricity demand growth rates.

1_SenScenario: Generates region- and fuel-specific electricity generation trajectories for the five major global regions, and interpolates them to the model’s temporal resolution.

2_GetPPInfor: Compiles unit-level power-plant information using the Global Infrastructure Emissions Detector (GID) dataset, extracting technical attributes (installed capacity, fuel consumption, generation, and age) and emissions for over 4,000 GW of global fossil-fuel power plants in 2024.

3_PPTurnover: Implements the unit-level turnover model, simulating future construction, retirement, and CCUS retrofitting of fossil power plants to quantify the impacts of renewable deployment and electricity demand growth.

4_FleetAnalysis: Analyzes power-sector outcomes under alternative renewable and demand growth rates, including fossil power capacity dynamics and the scale of CCUS deployment.

5_CostEmission: Analyzes power-sector outcomes under alternative renewable and demand growth rates, including levelized cost of electricity (LCOE) and cumulative and committed emissions.

We provide access to the full unit-level turnover model code. However, some model inputs are not publicly available, as they rely on technical attributes and emissions data derived from the GID dataset, which in turn incorporates proprietary databases from collaborators. These databases (e.g., WEPP) are subject to user license agreements that restrict public access.
