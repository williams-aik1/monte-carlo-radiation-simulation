import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pydicom

# -----------------------------
# App Branding
# -----------------------------
st.set_page_config(page_title="PhotonScope MC", layout="wide")
st.title("PhotonScope MC (Monte Carlo)")
st.markdown("**Monte Carlo Radiation Simulation with Tumor Targeting & Dose Visualization**")

# -----------------------------
# File Upload
# -----------------------------
uploaded_file = st.file_uploader("Upload CT DICOM file", type=["dcm"])

if uploaded_file is not None:
    ds = pydicom.dcmread(uploaded_file)
    image = ds.pixel_array.astype(float)

    # Convert to Hounsfield Units
    hu = image * ds.RescaleSlope + ds.RescaleIntercept

    # -----------------------------
    # Tissue Segmentation
    # -----------------------------
    tissue = np.zeros_like(hu)
    tissue[hu < -500] = 0           # Air
    tissue[(hu >= -500) & (hu < 300)] = 1  # Soft Tissue
    tissue[hu >= 300] = 2           # Bone

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
    st.sidebar.header("PhotonScope MC Controls")
    model = st.sidebar.selectbox("Simulation Model", ["Deterministic", "Monte Carlo"])
    I0 = st.sidebar.slider("Beam Intensity", 10, 200, 100)
    n_photons = st.sidebar.slider("Number of Photons", 100, 20000, 5000)

    # Add a professional footer in the sidebar
    st.sidebar.markdown(
       """
       <div style="position:fixed; bottom:10px; left:10px; font-size:12px; color:gray;">
           by Williams Kaphika
       </div>
       """,
      unsafe_allow_html=True
    )
        # -----------------------------
    # Tumor Region (centered in soft tissue)
    # -----------------------------
    soft_tissue_indices = np.argwhere(tissue == 1)
    tumor_center = soft_tissue_indices[len(soft_tissue_indices)//2]  # roughly center
    r_center, c_center = tumor_center
    tumor_radius = min(rows, cols)//20
    tumor_rows, tumor_cols = np.where(
        (np.arange(rows)[:, None] - r_center)**2 +
        (np.arange(cols)[None, :] - c_center)**2 <= tumor_radius**2
    )

    # -----------------------------
    # Simulation placeholders
    # -----------------------------
    dose_map = np.zeros_like(mu_map)
    dose_map_mc = np.zeros_like(mu_map)

    # -----------------------------
    # Deterministic Beam Simulation
    # -----------------------------
    if model == "Deterministic":
        for col in range(cols):
            beam_col = col
            intensity = I0
            for row in range(rows):
                mu = mu_map[row, beam_col]
                attenuation = np.exp(-mu)
                deposited = intensity * (1 - attenuation)
                dose_map[row, beam_col] += deposited
                intensity *= attenuation
                # small lateral scattering
                beam_col = min(max(beam_col + np.random.choice([-1,0,1]), 0), cols-1)
                if intensity < 1e-6:
                    break

    # -----------------------------
    # Monte Carlo Photon Transport
    # -----------------------------
    if model == "Monte Carlo":
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

    target_map = dose_map_mc if model == "Monte Carlo" else dose_map

    # -----------------------------
    # Tabs for Clean UI
    # -----------------------------
    tab1, tab2, tab3, tab4 = st.tabs(["CT Image", "Tissue Segmentation", "Dose Map", "Statistics"])

    # --- CT Image ---
    with tab1:
        fig1, ax1 = plt.subplots(figsize=(6,6))
        ax1.imshow(image, cmap="gray")
        ax1.set_title("CT Slice with Tumor")
        ax1.axis("off")
        ax1.plot(tumor_cols, tumor_rows, 'r.', markersize=1)
        st.pyplot(fig1)

    # --- Tissue Segmentation ---
    with tab2:
        fig2, ax2 = plt.subplots(figsize=(6,6))
        im2 = ax2.imshow(tissue, cmap="viridis")
        ax2.set_title("Tissue Segmentation")
        ax2.axis("off")
        fig2.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
        st.pyplot(fig2)

    # --- Dose Map with Tumor Overlay ---
    with tab3:
        fig3, ax3 = plt.subplots(figsize=(6,6))
        im3 = ax3.imshow(target_map, cmap="hot")
        ax3.set_title(f"{model} Dose Map")
        ax3.axis("off")
        ax3.plot(tumor_cols, tumor_rows, 'b.', markersize=1)
        fig3.colorbar(im3, ax=ax3, fraction=0.046, pad=0.04)
        st.pyplot(fig3)

    # --- Dose Statistics ---
    with tab4:
        st.subheader("Dose Statistics by Tissue")
        st.write("Air:", np.mean(target_map[tissue == 0]))
        st.write("Soft Tissue:", np.mean(target_map[tissue == 1]))
        st.write("Bone:", np.mean(target_map[tissue == 2]))

        st.subheader("Tumor Dose Analysis")
        tumor_dose = target_map[np.ix_(tumor_rows, tumor_cols)].flatten()
        threshold = 0.05
        underdose_prob = np.mean(tumor_dose < threshold)

        st.write("Mean Tumor Dose:", np.mean(tumor_dose))
        st.write("Tumor Dose Std Dev:", np.std(tumor_dose))
        st.write("Max Tumor Dose:", np.max(tumor_dose))
        st.write("Min Tumor Dose:", np.min(tumor_dose))
        st.write(f"Tumor Underdose Probability (<{threshold} dose):", underdose_prob)

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.header("PhotonScope MC Controls")
model = st.sidebar.selectbox("Simulation Model", ["Deterministic", "Monte Carlo"])
I0 = st.sidebar.slider("Beam Intensity", 10, 200, 100)
n_photons = st.sidebar.slider("Number of Photons", 100, 20000, 5000)

# Add a professional footer in the sidebar
st.sidebar.markdown(
    """
    <div style="position:fixed; bottom:10px; left:10px; font-size:12px; color:gray;">
        Developed by Williams Kaphika
    </div>
    """,
    unsafe_allow_html=True
)

