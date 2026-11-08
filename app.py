import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_utils import (
    load_csv,
    clean_numeric_data,
    get_lightcurve_stats,
    get_summary_values,
)

# --------------------------------------------------
# # 1. Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AstroLab | Exoplanet Explorer",
    page_icon="🔭",
    layout="wide",
)

st.title("🔭 AstroLab")
st.subheader("Exoplanet Transit Explorer")

st.caption(
    "NASA TESS | Pi Mensae (TIC 261136679) | Sector 1"
)

st.info(
    "Educational research prototype. "
    "The displayed results are preliminary BLS candidates, "
    "not confirmed new exoplanet discoveries."
)

# --------------------------------------------------
# # 2. Load datasets
# --------------------------------------------------

@st.cache_data
def load_all_data():
    lightcurve = load_csv("lightcurve")
    periodogram = load_csv("periodogram")
    phase = load_csv("phase")
    summary = load_csv("summary")

    return lightcurve, periodogram, phase, summary

try:
    lc_df, bls_df, phase_df, summary_df, = load_all_data()

    lc_df = clean_numeric_data(
        lc_df,
        ["time_btjd", "normalized_flux"]
    )

    bls_df = clean_numeric_data(
        bls_df,
        ["period_days", "bls_power"]
    )

    phase_df = clean_numeric_data(
        phase_df,
        ["phase", "normalized_flux"]
    )

    summary = get_summary_values(summary_df)
    stats = get_lightcurve_stats(lc_df)

    if bls_df.empty or phase_df.empty:
        raise ValueError("Periodogram or phase data is empty.")

except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
    st.error(f"Could not load AstroLab data: {error}")
    st.stop()

# --------------------------------------------------
# # 3. Sidebar controls
# --------------------------------------------------

st.sidebar.header("Dashboard Controls")

show_reference = st.sidebar.checkbox(
    "Show reference brightness",
    value=True
)

show_best_peroid = st.sidebar.checkbox(
    "Show best BLS period",
    value=True
)

point_size = st.sidebar.slider(
    "Light curve point size",
    min_value=1,
    max_value=10,
    value=3
)

st.sidebar.divider()

st.sidebar.markdown("**Data source**")
st.sidebar.write("NASA TESS / MAST")
st.sidebar.write("SPOC PDCSAP Light curve")
st.sidebar.write("Sector: 1")

# --------------------------------------------------
# Debug Mode
# --------------------------------------------------

debug_mode = st.sidebar.checkbox(
    "Developer Debug Mode",
    value=False
)

if debug_mode:
    st.sidebar.write("Light Curve shape:", lc_df.shape)
    st.sidebar.write("BLS shape:", bls_df.shape)
    st.sidebar.write("Phase shape:", phase_df.shape)
    st.sidebar.write("Summary shape:", summary_df.shape)

# --------------------------------------------------
# # 4. Summary metrics
# --------------------------------------------------

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Best BLS Period",
    f"{summary['best_period_days']:.4f} d"
)

col2.metric(
    "Transit Depth",
    f"{summary['best_depth'] * 100:.3f}%"
)

col3.metric(
    "Observations",
    f"{stats['count']:,}"
)

col4.metric(
    "Time Span",
    f"{stats['time_span_days']:.2f} d"
)

col5.metric(
    "Median Normalized Flux",
    f"{stats['median_flux']:.5f}"
)

# --------------------------------------------------
# # 5. Tabs
# --------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Light Curve",
    "BLS Periodogram",
    "Phase Folding",
    "Data Explorer",
])

# --------------------------------------------------
# Tab 1: Overview
# --------------------------------------------------

with tab1:
    st.header("Project Overview")

    st.write(
        "AstroLab analyzes a TESS light curve of Pi Mensae "
        "using Python and Box Least Squares (BLS). "
        "The goal is to investigate periodic transit-like "
        "brightness decreases."
    )

    st.markdown("### Analysis Workflow")

    st.markdown(
        "1. Retrieves TESS observations from MAST.\n"
        "2. Clean and normalize the light curve.\n"
        "3. Search trial obtibal periods using BLS.\n"
        "4. Visualize the periodogram and folded light curve.\n"
        "5. Compare results with published reference values."
    )

    st.markdown("### Scientific Limitations")

    st.warning(
        "BLS power is not a detection probability. "
        "Instrumental systematics, stellar variability, "
        "period aliases, and preprocessing may affect results."
    )

    if "reference+period_days_aprox" in summary_df.columns:
        reference = float(
            summary_df.iloc[0]["reference_period_days_approx"]
        )

        if np.isfinite(reference) and reference > 0:
            difference = abs(summary["best_period_days"] - reference)
            st.write(f"Approximate reference period: {reference:.3f}")
            st.write(f"Absolute period difference: {difference:.4f}")

# --------------------------------------------------
# Tab 2: Light Curve
# --------------------------------------------------

with tab2:
    st.header("TESS Light Curve")

    fig_lc = px.scatter(
        lc_df,
        x="time_btjd",
        y="normalized_flux",
        title="Pi Mensae - Normalized TESS Light Curve",
        labels={
            "time_btjd": "Time (BTJD)",
            "normalized_flux": "Normalized Flux",
        }
    )

    fig_his = px.histogram(
        lc_df,
        x="normalized_flux",
        nbins=60,
        title="Flux Distribution"
    )

    fig_lc.update_traces(
        marker=dict(size=point_size, opacity=0.65)
    )

    if show_reference:
        fig_lc.add_hline(
            y=1.0,
            line_dash="dash",
            line_color="red",
        )


    st.plotly_chart(fig_lc, use_container_width=True)
    st.plotly_chart(fig_his, use_container_width=True)

    st.markdown("### Light Curve Statistics")
    st.dataframe(
        pd.DataFrame([stats]),
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download Light Curve CSV",
        data=lc_df.to_csv(index=False).encode("utf-8"),
        file_name="astrolab_lightcurve.csv",
        mime="text/csv",
    )

# --------------------------------------------------
# Tab 3: BLS Periodogram
# --------------------------------------------------

with tab3:
    st.header("Box Least Squares Periodogram")

    ranked = bls_df.sort_values("bls_power", ascending=False)
    top=[]
    for _, row in ranked.iterrows():
        p=float(row["period_days"])
        if all(abs(p - old) > 0.15 for old in top):
            top.append(p)
        if len(top) == 5:
            break

    fig_bls = px.line(
        bls_df,
        x="period_days",
        y="bls_power",
        title="BLS Period Search",
        labels={
            "period_days": "Trial Period (days)",
            "bls_power": "BLS Power",
        },
    )

    if show_best_peroid:
        fig_bls.add_vline(
            x=summary["best_period_days"],
            line_dash="dash",
            line_color="red",
        )

    st.plotly_chart(fig_bls, use_container_width=True)
    st.dataframe(pd.DataFrame({"Candidate Period (days)": top}))

    st.write(
        "Best candidate period:",
        f"{summary['best_period_days']:.5f} days"
    )

    st.warning(
        "A high BLS peak alone does not confirm an exoplanet. "
        "Futher validation is required."
    )

    st.caption(
        "The highest BLS peak is a candidate model, "
        "not independent proof odf an exoplanet."
    )

    st.download_button(
        "Download BLS Periodogram",
        data=bls_df.to_csv(index=False).encode("utf-8"),
        file_name="astrolab_bls_periodogram.csv",
        mime="text/csv",
    )

# --------------------------------------------------
# Tab 4: Phase Folding
# --------------------------------------------------

with tab4:
    st.header("Phase-Folded Light Curve")

    phase_limit = st.slider(
        "Phase display range",
        min_value=0.02,
        max_value=0.50,
        value=0.10,
        step=0.01,
    )

    fig_phase = px.scatter(
        phase_df,
        x="phase",
        y="normalized_flux",
        title="Phase-Folded TESS Observations",
        labels={
            "phase": "Orbital Phase",
            "normalized_flux": "Normalized Flux"
        },
    )

    fig_phase.update_traces(
        marker=dict(size=3, opacity=0.4)
    )

    fig_phase.update_xaxes(
        range=[-phase_limit, phase_limit]
    )

    fig_phase.add_vline(
        x=0,
        line_dash="dash",
        line_color="red",
    )

    st.plotly_chart(fig_phase, use_container_width=True)

    st.write(
        "Estimated transit duration:",
        f"{summary['best_duration_days'] * 24:.2f}"
    )

    st.caption(
        "Phase values were calculated using the best BLS "
        "period and transit epoch from Day 4."
    )

# --------------------------------------------------
# Tab 5: Data Explorer
# --------------------------------------------------

with tab5:
    st.header("Data Explorer")

    dataset_name = st.selectbox(
        "Choose dataset",
        [
            "Light Curve",
            "BLS Periodogram",
            "Phase-Folded Data",
            "Detection Summary",
        ],
    )

    datasets={
        "Light Curve": lc_df,
        "BLS Periodogram": bls_df,
        "Phase-Folded Data": phase_df,
        "Detection Summary": summary_df,
    }

    selected_df = datasets[dataset_name]

    st.write("Rows:", len(selected_df))
    st.dataframe(selected_df, use_container_width=True)

    st.download_button(
        "Download Selected Dataset",
        data=selected_df.to_csv(index=False).encode("utf-8"),
        file_name="astrolab_selected_data.csv",
        mime="text/csv",
    )

# --------------------------------------------------
#  Footer
# --------------------------------------------------

st.divider()

st.caption(
    "AstroLab | Astronomy Data Analysis Porfolio | Data: NASA TESS / MAST | "
    "Built with Python, Pandas, Plotly and Streamlit"
)