# Unit-level-Turnover-Model
## Overview
The repository contains the code for the data-driven complement to energy-emissions model developed in the paper "Accelerating renewable deployment under rapid growth of electricity demand".

The model explicitly resolves unit-level fossil power plant dynamics to assess how alternative trajectories of renewable generation and electricity demand growth shape fossil capacity changes, CCUS deployment, and committed emissions.

We provide access to the full unit-level turnover model code. However, some model inputs are not publicly available, as they rely on technical attributes and emissions data derived from the Global Infrastructure Emissions Detector (GID) dataset, which in turn incorporates proprietary databases from collaborators. These databases (e.g., WEPP) are subject to user license agreements that restrict public access. Therefore, we adopt an illustrative dataset to demonstrate the model workflow and code implementation. Please note that this illustrative dataset is synthetic and should not be interpreted as representing real unit-level data.

If you are looking for more details, please contact yanxz22@mails.tsinghua.edu.cn or dantong@tsinghua.edu.cn.

## Software requirements
### OS Requirements
This model has been tested on the CentOS Linux 7 and Windows 11.

### Python Dependencies
This model has been tested on the following dependencies:
```bash
numpy==1.23.5
pandas==2.2.3
matplotlib== 3.7.1
seaborn==0.13.2
scipy==1.10.1
```

## Installation Guide
The model can be used directly after downloading the repository:
```bash
git clone https://github.com/yanxzh/Unit-level-Turnover-Model/
cd Unit-level-Turnover-Model/
```

## Module description
The codebase is organized into the following modules:

0_SetAndRun: Defines the core model settings, including the simulation period, and constructs a structured sensitivity grid spanning a broad range of renewable generation and electricity demand growth rates.

1_SenScenario: Generates electricity demand and generation trajectories for the five major global regions, and interpolates them to the model’s temporal resolution.

2_GetPPInfor: Compiles unit-level power-plant information using GID dataset, extracting technical attributes (installed capacity, fuel consumption, generation, and age) and emissions for over 4,000 GW of global fossil-fuel power plants in 2024.

3_PPTurnover: Implements the unit-level turnover model, simulating future construction, retirement, and CCUS retrofitting of fossil power plants to quantify the impacts of renewable deployment and electricity demand growth.

4_FleetAnalysis: Analyzes power-sector outcomes under alternative demand growth rates and fraction of renewable generation growth over electricity demand growth, including fossil power capacity changes and the scale of CCUS deployment.

5_Emission: Analyzes fossil committed emissions under alternative demand growth rates and fraction of renewable generation growth over electricity demand growth.

## Instructions for use
Future trajectories of sensitivity tests and llustrative unit-level dataset are provided in 1_SenScenario and 2_GetPPInfor, respectively.

To run the unit-level turnover model for a single sensitivity test, with a demand growth rate of 4% yr⁻¹ and 112.5% of demand growth met by renewables, use:
```bash
cd Unit-level-Turnover-Model/3_PPTurnover/scr
python S2_RunAll.py
```
The expected runtime for this test is approximately 1 minute.

The data of fossil power capacity changes and CCUS deployment across sensitivity tests can be visualized using:
```bash
cd Unit-level-Turnover-Model/4_FleetAnalysis/scr
python S1_Contour_CapacityChange.py
python S2_Contour_CarbonManagement.py
```

The data of fossil power committed emissions across sensitivity tests can be visualized using:
```bash
cd Unit-level-Turnover-Model/5_Emission/scr
python S2_Contour_Emmission.py
```

## License
This model is licensed under the MIT License.
