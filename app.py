import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pydicom

st.set_page_config(layout="wide")

st.title("🧠 Monte Carlo Radiation Therapy Simulation")
st.caption("Interactive Monte Carlo-based radiation therapy simulation using CT imaging")
# -----------------------------
# SIDEBAR CONTROLS (NEW 🔥)
# -----------------------------
st.sidebar.header("Simulation Controls")

n_photons = st.sidebar.slider("Number of Photons", 1000, 20000, 8000)
beam_sigma = st.sidebar.slider("Beam Focus (σ)", 1, 10, 3)
threshold = st.sidebar.slider("Underdose Threshold", 0.1, 0.8, 0.3)

# -----------------------------
# FILE UPLOAD
# -----------------------------
uploaded_file = st.file_uploader("Upload CT DICOM file", type=["dcm"])

if uploaded_file is not None:

    ds = pydicom.dcmread(uploaded_file)
    image = ds.pixel_array.astype(float)

    hu = image * ds.RescaleSlope + ds.RescaleIntercept

    # -----------------------------
    # SEGMENTATION
    # -----------------------------
    tissue = np.zeros_like(hu)
    tissue[hu < -500] = 0
    tissue[(hu >= -500) & (hu < 300)] = 1
    tissue[hu >= 300] = 2

    mu_map = np.zeros_like(tissue, dtype=float)
    mu_map[tissue == 0] = 0.02
    mu_map[tissue == 1] = 0.20
    mu_map[tissue == 2] = 0.50

    rows, cols = mu_map.shape

    # Tumor location
    soft_idx = np.argwhere(tissue == 1)
    r_center, c_center = soft_idx[len(soft_idx)//2]
    tumor_rows = range(r_center-10, r_center+10)
    tumor_cols = range(c_center-10, c_center+10)

    # -----------------------------
    # TABS
    # -----------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "🖼 CT & Segmentation",
        "📡 Deterministic",
        "🎲 Monte Carlo",
        "📊 Analysis"
    ])

    # =============================
    # TAB 1
    # =============================
    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots()
            ax.imshow(image, cmap="gray")
            ax.set_title("CT Image")
            ax.axis("off")
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots()
            ax.imshow(tissue, cmap="viridis")
            ax.set_title("Segmentation")
            ax.axis("off")
            st.pyplot(fig)

    # =============================
    # TAB 2: DETERMINISTIC
    # =============================
    with tab2:
        dose_map = np.zeros_like(mu_map)
        I0 = 100

        for col in range(cols):
            beam_col = col
            intensity = I0

            for row in range(rows):
                mu = mu_map[row, beam_col]
                attenuation = np.exp(-mu)
                deposited = intensity * (1 - attenuation)

                dose_map[row, beam_col] += deposited
                intensity *= attenuation

                beam_col = np.clip(beam_col + np.random.choice([-1,0,1]),0,cols-1)

                if intensity < 1e-6:
                    break

        fig, ax = plt.subplots()
        ax.imshow(dose_map, cmap="hot")
        ax.set_title("Deterministic Dose")
        ax.axis("off")
        st.pyplot(fig)

    # =============================
    # TAB 3: MONTE CARLO
    # =============================
    with tab3:
        dose_map_mc2 = np.zeros((rows, cols))

        for p in range(n_photons):
            x = int(np.random.normal(c_center, beam_sigma))
            x = np.clip(x, 0, cols - 1)

            y = 0
            energy = 1.0

            while energy > 0.001 and y < rows:
                mu = mu_map[y, x]
                if np.random.random() < (1 - np.exp(-mu)):

                    if (y in tumor_rows) and (x in tumor_cols):
                        deposited = energy * 0.2
                    else:
                        deposited = energy * 0.1

                    dose_map_mc2[y, x] += deposited
                    energy *= 0.9

                x = np.clip(x + np.random.choice([-1,0,1], p=[0.1,0.8,0.1]),0,cols-1)
                y += 1

        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots()
            ax.imshow(dose_map_mc2, cmap="hot")
            ax.set_title("Monte Carlo Dose")
            ax.axis("off")
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots()
            ax.imshow(dose_map_mc2, cmap="hot")

            for r in tumor_rows:
                for c in tumor_cols:
                    ax.plot(c, r, 'b.', markersize=1)

            ax.set_title("Tumor Targeting")
            ax.axis("off")
            st.pyplot(fig)

    # =============================
    # TAB 4: ANALYSIS DASHBOARD
    # =============================
    with tab4:

        tumor_dose_targeted = dose_map_mc2[np.ix_(tumor_rows, tumor_cols)].flatten()

        # Random beam
        dose_map_mc = np.zeros((rows, cols))
        for p in range(n_photons):
            x = np.random.randint(0, cols)
            y = 0
            energy = 1.0

            while energy > 0.001 and y < rows:
                mu = mu_map[y, x]
                if np.random.random() < (1 - np.exp(-mu)):
                    dose_map_mc[y, x] += energy * 0.1
                    energy *= 0.9

                x = np.clip(x + np.random.choice([-1,0,1]),0,cols-1)
                y += 1

        tumor_dose_random = dose_map_mc[np.ix_(tumor_rows, tumor_cols)].flatten()

        col1, col2 = st.columns(2)

        with col1:
            st.write("### Dose Distribution")
            fig, ax = plt.subplots()
            ax.hist(tumor_dose_targeted, bins=20)
            st.pyplot(fig)

        with col2:
            st.write("### Mean Dose Comparison")
            means = [np.mean(tumor_dose_random), np.mean(tumor_dose_targeted)]

            fig, ax = plt.subplots()
            ax.bar(["Random", "Targeted"], means)
            st.pyplot(fig)

        # Underdose calculation (LIVE 🔥)
        dose_norm = dose_map_mc2 / (np.max(dose_map_mc2) + 1e-8)
        tumor_norm = dose_norm[np.ix_(tumor_rows, tumor_cols)].ravel()

        underdose_prob = np.mean(tumor_norm < threshold)

        st.metric("Tumor Underdose Probability", f"{underdose_prob:.3f}")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("""
<style>
.footer {
    position: fixed;
    bottom: 10px;
    left: 10px;
    font-size: 12px;
    color: gray;
}
</style>

<div class="footer">
Developed by <b>Williams Stonard Kaphika</b><br>
⚠️ Educational simulation — not for clinical use
</div>
""", unsafe_allow_html=True)
