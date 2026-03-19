# Monte Carlo Radiation Simulation using CT Data

## Overview
This project simulates radiation dose deposition in human tissue using real CT scan data.

It compares:
- Deterministic radiation attenuation (Beer–Lambert law)
- Monte Carlo photon transport (stochastic simulation)

## Features
- CT DICOM image processing using pydicom
- Tissue segmentation (Air, Soft Tissue, Bone)
- Radiation attenuation modeling
- Monte Carlo photon random walk simulation
- Tumor region modeling
- Beam targeting simulation
- Dose statistics and visualization

## Results
- Bone absorbs the highest radiation dose
- Monte Carlo simulation produces realistic stochastic patterns
- Targeted beams significantly increase tumor dose
- Underdose probability decreases with beam focusing

## Example Outputs
- CT image visualization
- Tissue segmentation map
- Radiation dose heatmaps
- Tumor dose distribution
- Beam comparison plots

## Technologies Used
- Python
- NumPy
- Matplotlib
- Pandas
- pydicom

## Project Structure
├── radiation_simulation.ipynb
├── radiation_simulation_report.pdf
└── README.md
## Future Improvements
- 3D CT simulation
- Advanced scattering physics
- Integration with Geant4

## Author
WILLIAMS STONARD KAPHIKA
