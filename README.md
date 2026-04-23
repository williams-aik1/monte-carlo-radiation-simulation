# CT-Based Monte Carlo Radiation Dose Simulation

## Overview

This project simulates **radiation dose deposition in human tissue** using real CT (DICOM) images. It compares a simple deterministic beam model with a **Monte Carlo photon transport simulation** to demonstrate how beam targeting improves tumor dose delivery.

The application includes an interactive web interface built with Streamlit, allowing users to upload CT scans and visualize radiation dose distribution in real time.

---

## Objectives

* Simulate radiation transport through human tissue
* Compare deterministic vs stochastic (Monte Carlo) models
* Analyze dose deposition across different tissue types
* Evaluate tumor targeting efficiency and underdose probability

---

## Features

* 📂 Upload real CT DICOM images
* 🧬 Automatic tissue segmentation (Air, Soft Tissue, Bone)
* ⚛️ Monte Carlo photon transport simulation
* 🎯 Tumor region detection and targeted beam delivery
* 🔥 Dose heatmap visualization
* 📊 Statistical analysis of dose distribution
* 📉 Tumor underdose probability calculation
* 🌐 Interactive Streamlit web app

---

## Outputs

* CT image visualization
  <img width="389" height="411" alt="CT Slice" src="https://github.com/user-attachments/assets/c58b31e8-d1b0-4717-b6dc-81d0d633e773" />
  <img width="525" height="435" alt="Hounsfield Units" src="https://github.com/user-attachments/assets/5f80ab86-71d6-4aa8-96d5-ccbe189f6505" />

* Tissue segmentation map
  <img width="509" height="435" alt="Tissue Segmentation" src="https://github.com/user-attachments/assets/2e8cbf3a-d247-45c0-849f-e1455582f900" />

* Radiation dose heatmap
* Tumor overlay
* Dose distribution histogram
* Random vs targeted beam comparison

---

## Technical Approach

### 1. Hounsfield Unit Conversion

CT pixel values are converted to physical density using:

```
HU = pixel_value × slope + intercept
```

---

### 2. Tissue Segmentation

| Tissue Type | HU Range    |
| ----------- | ----------- |
| Air         | HU < -500   |
| Soft Tissue | -500 to 300 |
| Bone        | HU ≥ 300    |
<img width="525" height="435" alt="Hounsfield Units" src="https://github.com/user-attachments/assets/d11dbcb1-2005-4e46-a2bc-9bdfb4937da0" />

---

### 3. Radiation Attenuation Model

Each tissue type is assigned an attenuation coefficient:

| Tissue      | μ (attenuation) |
| ----------- | --------------- |
| Air         | 0.02            |
| Soft Tissue | 0.20            |
| Bone        | 0.50            |

Radiation follows exponential attenuation:

```
I = I₀ · exp(-μx)
```

---

### 4. Monte Carlo Simulation

Photons are simulated individually with:

* Random interactions based on probability:

  ```
  P(interaction) = 1 - exp(-μ)
  ```
* Energy deposition at interaction points
* Random lateral scattering
* Energy decay after each interaction

---

### 5. Tumor Targeting

* Tumor region defined within soft tissue
* Targeted beam focuses photons near tumor
* Increased energy deposition inside tumor region

---

## 📊 Results & Insights

### 🔬 Key Findings

* Targeted beam delivers **~40× higher tumor dose** compared to random beam
* Monte Carlo simulation produces realistic stochastic dose patterns
* Soft tissue absorbs the highest radiation dose
* Bone shows minimal dose due to high attenuation

### 📉 Tumor Analysis

* Mean tumor dose significantly increases with targeting
* Underdose probability ≈ **40%**, showing dose variability

---

## 🛠️ Tech Stack

* Python
* NumPy
* Matplotlib
* Pydicom
* Pandas
* Streamlit

---

## 🌐 Running the App

### 🔧 Install dependencies

```
pip install -r requirements.txt
```

### ▶️ Run locally

```
streamlit run app.py
```

---

### ☁️ Run in Google Colab

```
!streamlit run app.py & npx localtunnel --port 8501
```

---

## 📁 Project Structure

```
project/
│── app.py
│── README.md
│── requirements.txt
│── images/
│── sample_data/
```

---

## 📌 Future Improvements

* 3D CT volume simulation (multi-slice)
* Dose Volume Histogram (DVH)
* Beam angle optimization
* Real-world dose units (Gray)
* Energy-dependent photon interactions

---

## 💡 Applications

* Radiation therapy planning (conceptual)
* Medical physics education
* Monte Carlo simulation learning
* Biomedical engineering projects

---

## ⚠️ Disclaimer

This project is for **educational and research purposes only**.
It is not intended for clinical use or medical decision-making.
---

## 👤 Author

Williams Stonard Kaphika
---

## Acknowledgments

* TCIA (The Cancer Imaging Archive) for CT datasets
* Open-source Python libraries
---

## Contact

kaphika.ws@gmail.com, htpps://www.linkedin.com/in/williamskaphika 
