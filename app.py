import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pydicom
import pandas as pd

st.set_page_config(layout="wide")
st.title("Monte Carlo Radiation Dose Simulation (CT-Based)")

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.header("Simulation Parameters")
n_photons = st.sidebar.slider("Number of Photons", 1000, 30000, 15000)
beam_sigma = st.sidebar.slider("Beam Focus (sigma)", 1, 10, 3)
threshold = st.sidebar.slider("Underdose Threshold", 0.0, 1.0, 0.3)

# -----------------------------
# File Upload
# -----------------------------
uploaded_file = st.file_uploader("Upload CT DICOM file", type=["dcm"])

if uploaded_file is not None:

    ds = pydicom.dcmread(uploaded_file)
    image = ds.pixel_array.astype(float)

    # -----------------------------
    # Convert to HU
    # -----------------------------
    hu = image * ds.RescaleSlope + ds.RescaleIntercept

    # -----------------------------
    # Tissue Segmentation
    # -----------------------------
    tissue = np.zeros_like(hu)
    tissue[hu < -500] = 0
    tissue[(hu >= -500) & (hu < 300)] = 1
    tissue[hu >= 300] = 2

    # -----------------------------
    # Attenuation Map
    # -----------------------------
    mu_map = np.zeros_like(tissue, dtype=float)
    mu_map[tissue == 0] = 0.02
    mu_map[tissue == 1] = 0.20
    mu_map[tissue == 2] = 0.50

    rows, cols = mu_map.shape

    # -----------------------------
    # Tumor Selection (center of soft tissue)
    # -----------------------------
    soft_indices = np.argwhere(tissue == 1)
    center_index = len(soft_indices) // 2
    r_center, c_center = soft_indices[center_index]

    # -----------------------------
    # Monte Carlo (Targeted)
    # -----------------------------
    dose_map_mc2 = np.zeros((rows, cols))

    for p in range(n_photons):
        x = int(np.random.normal(c_center, beam_sigma))
        x = np.clip(x, 0, cols - 1)
        y = 0
        energy = 1.0

        while energy > 0.001 and y < rows:
            mu = mu_map[y, x]
            p_interact = 1 - np.exp(-mu)

            if np.random.random() < p_interact:
                if (r_center-10 <= y < r_center+10) and (c_center-10 <= x < c_center+10):
                    deposited = energy * 0.2
                else:
                    deposited = energy * 0.1

                dose_map_mc2[y, x] += deposited
                energy *= 0.9

            step = np.random.choice([-1, 0, 1], p=[0.1, 0.8, 0.1])
            x = np.clip(x + step, 0, cols - 1)
            y += 1

    # -----------------------------
    # Monte Carlo (Random)
    # -----------------------------
    dose_map_mc = np.zeros((rows, cols))

    for p in range(n_photons):
        x = np.random.randint(0, cols)
        y = 0
        energy = 1.0

        while energy > 0.001 and y < rows:
            mu = mu_map[y, x]
            p_interact = 1 - np.exp(-mu)

            if np.random.random() < p_interact:
                deposited = energy * 0.1
                dose_map_mc[y, x] += deposited
                energy *= 0.9

            step = np.random.choice([-1, 0, 1])
            x = np.clip(x + step, 0, cols - 1)
            y += 1

    # -----------------------------
    # Tumor Dose Analysis
    # -----------------------------
    dose_norm = dose_map_mc2 / (np.max(dose_map_mc2) + 1e-8)
    tumor_dose = dose_norm[r_center-10:r_center+10, c_center-10:c_center+10].ravel()
    underdose_prob = np.mean(tumor_dose < threshold)

    tumor_dose_random = dose_map_mc[r_center-10:r_center+10, c_center-10:c_center+10].ravel()
    tumor_dose_targeted = dose_map_mc2[r_center-10:r_center+10, c_center-10:c_center+10].ravel()

    # -----------------------------
    # Layout
    # -----------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("CT Image")
        fig1, ax1 = plt.subplots()
        ax1.imshow(image, cmap='gray')
        ax1.axis('off')
        st.pyplot(fig1)

        st.subheader("Tissue Segmentation")
        fig2, ax2 = plt.subplots()
        ax2.imshow(tissue, cmap='viridis')
        st.pyplot(fig2)

    with col2:
        st.subheader("Monte Carlo Dose (Targeted)")
        fig3, ax3 = plt.subplots()
        ax3.imshow(dose_map_mc2, cmap='hot')
        st.pyplot(fig3)

        st.subheader("Tumor Overlay")
        fig4, ax4 = plt.subplots()
        ax4.imshow(dose_map_mc2, cmap='hot')
        for r in range(r_center-10, r_center+10):
            for c in range(c_center-10, c_center+10):
                ax4.plot(c, r, 'b.', markersize=1)
        st.pyplot(fig4)

    # -----------------------------
    # Charts
    # -----------------------------
    st.subheader("Tumor Dose Distribution")
    fig5, ax5 = plt.subplots()
    ax5.hist(tumor_dose, bins=20)
    st.pyplot(fig5)

    st.subheader("Random vs Targeted Beam")
    fig6, ax6 = plt.subplots()
    labels = ["Random", "Targeted"]
    means = [np.mean(tumor_dose_random), np.mean(tumor_dose_targeted)]
    ax6.bar(labels, means)
    st.pyplot(fig6)

    # -----------------------------
    # Metrics
    # -----------------------------
    st.subheader("Key Metrics")
    st.write("Mean Tumor Dose (Targeted):", np.mean(tumor_dose_targeted))
    st.write("Mean Tumor Dose (Random):", np.mean(tumor_dose_random))
    st.write("Underdose Probability:", underdose_prob)

    df = pd.DataFrame({
        "Metric": ["Mean", "Std", "Max", "Min"],
        "Tumor Dose": [
            np.mean(tumor_dose),
            np.std(tumor_dose),
            np.max(tumor_dose),
            np.min(tumor_dose)
        ]
    })

    st.dataframe(df)

else:
    st.info("Please upload a DICOM (.dcm) file to begin simulation.")
