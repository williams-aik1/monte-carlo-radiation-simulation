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
  <img width="389" height="411" alt="CT Slice" src="https://github.com/user-attachments/assets/c58b31e8-d1b0-4717-b6dc-81d0d633e773" /><img width="525" height="435" alt="Hounsfield Units" src="https://github.com/user-attachments/assets/5f80ab86-71d6-4aa8-96d5-ccbe189f6505" />
<img width="477" height="75" alt="image" src="https://github.com/user-attachments/assets/6ead4872-e0e6-4ee6-a46d-95b7b8e2939d" />

* Tissue segmentation map
  <img width="509" height="435" alt="Tissue Segmentation" src="https://github.com/user-attachments/assets/2e8cbf3a-d247-45c0-849f-e1455582f900" />

* Radiation dose heatmap
  <img width="496" height="435" alt="image" src="https://github.com/user-attachments/assets/b95736ca-50ab-4dc8-9a55-a1a7d54a0cc4" />

* Tumor overlay
  <img width="430" height="435" alt="image" src="https://github.com/user-attachments/assets/4a681290-4c46-40d7-8b9b-8cacbf0c203f" />


* Dose distribution histogram
  <img width="543" height="435" alt="image" src="https://github.com/user-attachments/assets/de68e5c8-2681-4179-b40e-e8f3b95d8d9f" />

* Random vs targeted beam comparison
<img width="567" height="435" alt="image" src="https://github.com/user-attachments/assets/fef18c13-3b01-404a-8ac6-cbe67784d453" /> <img width="491" height="94" alt="image" src="https://github.com/user-attachments/assets/8e6f8493-9244-4241-a430-c41153f7b202" /> <img width="413" height="68" alt="image" src="https://github.com/user-attachments/assets/3a322cb0-ba0c-4567-8734-8f314273e9ff" />



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
| Bone        | 0.50            |<img width="491" height="126" alt="image" src="https://github.com/user-attachments/assets/bb745e22-5253-4c81-8a93-45d69be00c77" />


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
