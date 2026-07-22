"""CanvasGen Streamlit Web Application Entrypoint (Stage 1 Foundation).

Provides UI dashboard for system diagnostics, configuration inspection,
engine state verification, and roadmap previews for future stages.
"""

import streamlit as st
from config.settings import get_settings
from services.generation_service import GenerationService
from utils.logger import get_logger
from utils.memory import get_ram_usage, get_vram_usage

logger = get_logger("CanvasGen.App")

st.set_page_config(
    page_title="CanvasGen - AI Image Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    """Main application layout renderer."""
    settings = get_settings()
    service = GenerationService(settings=settings)

    st.title("🎨 CanvasGen - AI Image Generation Engine")
    st.caption("Production Ready Modular Architecture • Stage 1 Initialized")

    st.markdown("---")

    # System Status & Diagnostic Metrics Banner
    st.subheader("📊 System Diagnostic & Environment Status")
    col1, col2, col3, col4 = st.columns(4)

    ram_stats = get_ram_usage()
    vram_stats = get_vram_usage()

    with col1:
        st.metric(label="Environment", value=settings.app_env.upper())
    with col2:
        st.metric(label="Target Device", value=settings.device.upper())
    with col3:
        st.metric(
            label="System RAM",
            value=f"{ram_stats['used_mb']} MB",
            delta=f"{ram_stats['percent_used']}% Used",
        )
    with col4:
        vram_label = (
            f"{vram_stats['allocated_mb']} MB"
            if vram_stats["cuda_available"]
            else "CPU Mode"
        )
        st.metric(label="VRAM Allocated", value=vram_label)

    st.markdown("---")

    # Sidebar Configurations
    st.sidebar.header("⚙️ CanvasGen Configuration")
    st.sidebar.text_input("Active Model ID", value=settings.model_id, disabled=True)
    st.sidebar.selectbox("Precision", options=["fp16", "fp32", "bf16"], index=0)
    st.sidebar.selectbox(
        "Scheduler",
        options=service.scheduler_manager.list_available_schedulers(),
        index=0,
    )
    st.sidebar.markdown("---")
    st.sidebar.info("📌 Stage 1: Engine Skeletons & Verification Active")

    # Main View Tabs
    tab_overview, tab_config, tab_engine = st.tabs(
        ["🚀 Stage 1 Overview", "⚙️ Active Config", "⚡ Engine Capabilities"]
    )

    with tab_overview:
        st.success("✅ **Stage 1 Complete**: Architecture, engine modules, utilities, and tests are verified.")
        st.markdown(
            """
            ### 🌟 CanvasGen Capabilities Preview
            - **Text-to-Image**: High quality diffusion image synthesis.
            - **Batch Generation**: Multi-sample generation with seed sequence tracking.
            - **Scheduler Comparison**: Live quality/speed benchmark across DPM, Euler, DDIM, LMS.
            - **Inpainting**: Precise masked region replacement.
            - **Outpainting**: Directional canvas extension with background synthesis.
            """
        )

    with tab_config:
        st.subheader("Current Settings Dump")
        st.json(settings.model_dump(mode="json"))

    with tab_engine:
        st.subheader("Engine Component Verification")
        if st.button("🧪 Run Engine Test Synthesis (Stage 1 Mock)"):
            with st.spinner("Generating sample..."):
                img, path = service.generate_text_to_image(
                    prompt="A beautiful serene mountain landscape at sunset, 8k render",
                    save_output=True,
                )
                st.image(img, caption="Stage 1 Engine Placeholder Output", width=384)
                st.info(f"Artifact saved to: `{path}`")


if __name__ == "__main__":
    main()
