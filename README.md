# Unit-level-Turnover-Model
The repository contains the code for the data-driven complement to energy-emissions model developed in the paper "Rapid growth of electricity demand is forestalling phase-out of fossil generation".

The model explicitly resolves unit-level fossil power plant dynamics to assess how alternative trajectories of renewable generation and electricity demand growth shape fossil capacity evolution, CCUS deployment, and committed emissions.

The codebase is organized into the following modules:

0_SetAndRun: Defines the core model settings, including the simulation period, and constructs a structured sensitivity grid spanning a broad range of renewable generation and electricity demand growth rates.

1_SenScenario: Generates region- and fuel-specific electricity generation trajectories for the five major global regions, and interpolates them to the model’s temporal resolution.

2_GetPPInfor: Compiles unit-level power-plant information using the Global Infrastructure Emissions Detector (GID) dataset, extracting technical attributes (installed capacity, fuel consumption, generation, and age) and emissions for over 4,000 GW of global fossil-fuel power plants in 2024.

3_PPTurnover: Implements the unit-level turnover model, simulating future construction, retirement, and CCUS retrofitting of fossil power plants to quantify the impacts of renewable deployment and electricity demand growth.

4_FleetAnalysis: Analyzes power-sector outcomes under alternative demand growth rates and fraction of renewable generation growth over electricity demand growth, including fossil power capacity dynamics and the scale of CCUS deployment.

5_Emission: Analyzes fossil committed emissions under alternative demand growth rates and fraction of renewable generation growth over electricity demand growth.

We provide access to the full unit-level turnover model code. However, some model inputs are not publicly available, as they rely on technical attributes and emissions data derived from the GID dataset, which in turn incorporates proprietary databases from collaborators. These databases (e.g., WEPP) are subject to user license agreements that restrict public access.

If you are looking for more details, please contact yanxz22@mails.tsinghua.edu.cn or dantong@tsinghua.edu.cn.
