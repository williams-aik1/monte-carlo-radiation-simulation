import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pydicom

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(layout="wide", page_title="Radiation Simulation")

st.title("Monte Carlo Radiation Dose Simulation")

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.header("Simulation Controls")

n_photons = st.sidebar.slider("Number of Photons", 1000, 20000, 5000, step=1000)
beam_sigma = st.sidebar.slider("Beam Focus (Sigma)", 1, 10, 3)

# -----------------------------
# Upload DICOM
# -----------------------------
uploaded_file = st.file_uploader("Upload CT DICOM file", type=["dcm"])

if uploaded_file:

    ds = pydicom.dcmread(uploaded_file)
    image = ds.pixel_array.astype(float)

    # 🔥 Speed optimization (downsample)
    image = image[::2, ::2]

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
    # Tumor Region
    # -----------------------------
    soft_tissue_indices = np.argwhere(tissue == 1)
    r_center, c_center = soft_tissue_indices[len(soft_tissue_indices)//2]

    tumor_rows = range(r_center-10, r_center+10)
    tumor_cols = range(c_center-10, c_center+10)

    # -----------------------------
    # Deterministic Model
    # -----------------------------
    def deterministic_sim(mu_map):
        I0 = 100
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

                beam_col = np.clip(beam_col + np.random.choice([-1,0,1]), 0, cols-1)

                if intensity < 1e-6:
                    break

        return dose_map

    # -----------------------------
    # Monte Carlo (CACHED)
    # -----------------------------
    @st.cache_data(show_spinner=True)
    def monte_carlo(mu_map, r_center, c_center, n_photons, beam_sigma):
        dose_map = np.zeros((rows, cols))

        for p in range(n_photons):
            x = int(np.random.normal(c_center, beam_sigma))
            x = np.clip(x, 0, cols - 1)

            y = 0
            energy = 1.0

            while energy > 0.001 and y < rows:
                mu = mu_map[y, x]
                p_interact = 1 - np.exp(-mu)

                if np.random.random() < p_interact:

                    if (y in tumor_rows) and (x in tumor_cols):
                        deposited = energy * 0.2
                    else:
                        deposited = energy * 0.1

                    dose_map[y, x] += deposited
                    energy *= 0.9

                step = np.random.choice([-1,0,1], p=[0.1,0.8,0.1])
                x = np.clip(x + step, 0, cols-1)
                y += 1

        return dose_map

    # Run simulations
    dose_det = deterministic_sim(mu_map)
    dose_mc = monte_carlo(mu_map, r_center, c_center, n_photons, beam_sigma)

    # -----------------------------
    # Layout Tabs
    # -----------------------------
    tab1, tab2, tab3 = st.tabs(["CT & Tissue", "Deterministic", "Monte Carlo"])

    # -----------------------------
    # TAB 1: CT + Tissue
    # -----------------------------
    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots(figsize=(4,4))
            ax.imshow(hu, cmap="gray")
            ax.set_title("CT Image (HU)")
            ax.axis("off")
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots(figsize=(4,4))
            ax.imshow(tissue, cmap="viridis")
            ax.set_title("Tissue Segmentation")
            ax.axis("off")

            for r in tumor_rows:
                for c in tumor_cols:
                    ax.plot(c, r, 'r.', markersize=1)

            st.pyplot(fig)

    # -----------------------------
    # TAB 2: Deterministic
    # -----------------------------
    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots(figsize=(4,4))
            ax.imshow(dose_det, cmap="hot")
            ax.set_title("Dose Map")
            ax.axis("off")
            st.pyplot(fig)

        with col2:
            st.subheader("Statistics")
            st.write("Mean Dose:", np.mean(dose_det))
            st.write("Max Dose:", np.max(dose_det))
            st.write("Min Dose:", np.min(dose_det))

    # -----------------------------
    # TAB 3: Monte Carlo
    # -----------------------------
    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots(figsize=(4,4))
            ax.imshow(dose_mc, cmap="hot")
            ax.set_title("Monte Carlo Dose")
            ax.axis("off")

            for r in tumor_rows:
                for c in tumor_cols:
                    ax.plot(c, r, 'b.', markersize=1)

            st.pyplot(fig)

        with col2:
            st.subheader("Tumor Analysis")

            dose_norm = dose_mc / (np.max(dose_mc) + 1e-8)
            tumor_dose = dose_norm[np.ix_(tumor_rows, tumor_cols)].ravel()

            underdose_prob = np.mean(tumor_dose < 0.3)

            st.write("Mean Tumor Dose:", np.mean(tumor_dose))
            st.write("Underdose Probability:", underdose_prob)

            fig, ax = plt.subplots(figsize=(4,3))
            ax.hist(tumor_dose, bins=20)
            ax.set_title("Tumor Dose Distribution")
            st.pyplot(fig)

# -----------------------------
# Footer
# -----------------------------
st.markdown("""
<style>
.footer {
    position: fixed;
    left: 10px;
    bottom: 10px;
    font-size: 12px;
    color: gray;
}
</style>

<div class="footer">
Developed by <b>Williams Stonard Kaphika</b><br>
⚠️ Educational simulation only — not for clinical use
</div>
""", unsafe_allow_html=True)
