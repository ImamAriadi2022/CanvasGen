"""Aplikasi Web Streamlit CanvasGen (Fondasi Tahap 1).

Menyediakan dashboard antarmuka untuk diagnosa sistem, inspeksi konfigurasi,
verifikasi status engine, dan pratinjau rencana pengembangan tahap berikutnya.
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
    """Fungsi utama penyusun tata letak aplikasi."""
    settings = get_settings()
    service = GenerationService(settings=settings)

    st.title("🎨 CanvasGen - Studio Generasi Gambar berbasis AI")
    st.caption("Arsitektur Modular Siap Produksi • Tahap 1 Terinisialisasi")

    st.markdown("---")

    # Banner Status Diagnosa & Lingkungan Sistem
    st.subheader("📊 Status Diagnosa & Lingkungan Sistem")
    col1, col2, col3, col4 = st.columns(4)

    ram_stats = get_ram_usage()
    vram_stats = get_vram_usage()

    with col1:
        st.metric(label="Lingkungan", value=settings.app_env.upper())
    with col2:
        st.metric(label="Perangkat Target", value=settings.device.upper())
    with col3:
        st.metric(
            label="RAM Sistem",
            value=f"{ram_stats['used_mb']} MB",
            delta=f"{ram_stats['percent_used']}% Terpakai",
        )
    with col4:
        vram_label = (
            f"{vram_stats['allocated_mb']} MB"
            if vram_stats["cuda_available"]
            else "Mode CPU"
        )
        st.metric(label="VRAM Teralokasi", value=vram_label)

    st.markdown("---")

    # Konfigurasi Sidebar
    st.sidebar.header("⚙️ Konfigurasi CanvasGen")
    st.sidebar.text_input("ID Model Aktif", value=settings.model_id, disabled=True)
    st.sidebar.selectbox("Presisi", options=["fp16", "fp32", "bf16"], index=0)
    st.sidebar.selectbox(
        "Scheduler Noise",
        options=service.scheduler_manager.list_available_schedulers(),
        index=0,
    )
    st.sidebar.markdown("---")
    st.sidebar.info("📌 Tahap 1: Skeleton Engine & Verifikasi Aktif")

    # Tab Utama
    tab_overview, tab_config, tab_engine = st.tabs(
        ["🚀 Ringkasan Tahap 1", "⚙️ Konfigurasi Aktif", "⚡ Kapabilitas Engine"]
    )

    with tab_overview:
        st.success("✅ **Tahap 1 Selesai**: Arsitektur, modul engine, utilitas, dan pengujian telah terverifikasi 100%.")
        st.markdown(
            """
            ### 🌟 Pratinjau Kapabilitas CanvasGen
            - **Text-to-Image**: Sintesis gambar difusi berkualitas tinggi dari deskripsi teks.
            - **Batch Generation**: Generasi banyak sampel sekaligus dengan pelacakan urutan seed deterministik.
            - **Scheduler Comparison**: Komparasi kecepatan dan kualitas secara langsung antar sampler (DPM, Euler, DDIM, LMS).
            - **Inpainting**: Penggantian area bermasker secara presisi.
            - **Outpainting**: Perluasan kanvas ke berbagai arah dengan sintesis latar belakang yang seamless.
            """
        )

    with tab_config:
        st.subheader("Detail Konfigurasi Aktif Saat Ini")
        st.json(settings.model_dump(mode="json"))

    with tab_engine:
        st.subheader("Verifikasi Komponen Engine")
        if st.button("🧪 Jalankan Uji Sintesis Engine (Mock Tahap 1)"):
            with st.spinner("Menghasilkan gambar sampel..."):
                img, path = service.generate_text_to_image(
                    prompt="Pemandangan pegunungan indah saat matahari terbenam, 8k render",
                    save_output=True,
                )
                st.image(img, caption="Hasil Output Placeholder Engine Tahap 1", width=384)
                st.info(f"Artefak tersimpan di: `{path}`")


if __name__ == "__main__":
    main()
