import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pydicom

st.title("Monte Carlo Radiation Simulation")

# -----------------------------
# File Upload
# -----------------------------
uploaded_file = st.file_uploader("Upload CT DICOM file", type=["dcm"])

if uploaded_file is not None:

    ds = pydicom.dcmread(uploaded_file)
    image = ds.pixel_array.astype(float)

    st.subheader("CT Image")
    st.image(image, clamp=True)

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

    st.subheader("Tissue Segmentation")
    st.image(tissue, clamp=True)

    # -----------------------------
    # Attenuation Map
    # -----------------------------
    mu_map = np.zeros_like(tissue, dtype=float)

    mu_map[tissue == 0] = 0.02
    mu_map[tissue == 1] = 0.20
    mu_map[tissue == 2] = 0.50

    rows, cols = mu_map.shape

    # -----------------------------
    # Sidebar Controls
    # -----------------------------
    st.sidebar.header("Simulation Settings")

    model = st.sidebar.selectbox(
        "Choose Model",
        ["Deterministic", "Monte Carlo"]
    )

    I0 = st.sidebar.slider("Beam Intensity", 10, 200, 100)

    n_photons = st.sidebar.slider("Number of Photons", 100, 20000, 5000)

    # -----------------------------
    # Deterministic Simulation
    # -----------------------------
    if model == "Deterministic":

        dose_map = np.zeros_like(mu_map)

        for col in range(cols):
            beam_col = col
            intensity = I0

            for row in range(rows):
                mu = mu_map[row, beam_col]

                attenuation = np.exp(-mu)
                deposited = intensity * (1 - attenuation)

                dose_map[row, beam_col] += deposited
                intensity *= attenuation

                beam_col = min(max(beam_col + np.random.choice([-1,0,1]),0),cols-1)

                if intensity < 1e-6:
                    break

        st.subheader("Deterministic Dose Map")
        st.image(dose_map, clamp=True)

    # -----------------------------
    # Monte Carlo Simulation
    # -----------------------------
    if model == "Monte Carlo":

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
                x = min(max(x + step, 0), cols - 1)

                y += 1

        st.subheader("Monte Carlo Dose Map")
        st.image(dose_map_mc, clamp=True)

        # -----------------------------
        # Tissue Statistics
        # -----------------------------
        st.subheader("Dose Statistics")

        st.write("Air:", np.mean(dose_map_mc[tissue == 0]))
        st.write("Soft Tissue:", np.mean(dose_map_mc[tissue == 1]))
        st.write("Bone:", np.mean(dose_map_mc[tissue == 2]))
