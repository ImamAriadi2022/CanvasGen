"""CanvasGen - Aplikasi Web Generasi Gambar Berbasis AI menggunakan Streamlit."""

import io
from typing import Optional
from PIL import Image, ImageDraw
import streamlit as st

from config.settings import get_settings
from services.generation_service import GenerationService
from utils.memory import flush_vram, get_vram_usage

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="CanvasGen - Studio Gambar AI",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Gaya Tampilan Kustom (CSS)
st.markdown(
    """
    <style>
    .title-text {
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #3B82F6, #8B5CF6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stButton>button {
        font-weight: 700;
        border-radius: 8px;
        height: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_service_instance() -> GenerationService:
    """Menginisialisasi dan menyimpan cache instance GenerationService."""
    settings = get_settings()
    return GenerationService(settings=settings)


# Inisialisasi State Sesi Streamlit
if "generated_images" not in st.session_state:
    st.session_state["generated_images"] = []
if "current_image" not in st.session_state:
    st.session_state["current_image"] = None

# Navigasi Sidebar
with st.sidebar:
    st.title("⚙️ Navigasi Studio")
    mode_selection = st.radio(
        "Mode Aplikasi",
        ["🎨 Generasi Gambar (Text-to-Image)", "🖼️ Pengeditan Gambar (Inpaint & Outpaint)", "🛠️ Pengaturan & Memori Sistem"],
    )
    st.divider()
    vram = get_vram_usage()
    st.caption(f"Perangkat Target: {vram.get('device_name', 'CUDA/CPU')}")
    if st.button("🧹 Bersihkan VRAM Memory"):
        flush_vram()
        st.success("Memori VRAM GPU Berhasil Dibersihkan!")

# ==============================================================================
# MODE 1: GENERASI GAMBAR (TEXT-TO-IMAGE)
# ==============================================================================
if mode_selection == "🎨 Generasi Gambar (Text-to-Image)":
    st.markdown('<div class="title-text">CanvasGen AI Studio</div>', unsafe_allow_html=True)

    # 1. Prompt Teks
    prompt = st.text_area(
        "Prompt Teks",
        value="Pemandangan indah pegunungan saat matahari terbenam dengan danau jernih, gaya lukisan minyak, 8k",
        height=100,
        placeholder="Masukkan deskripsi gambar yang ingin Anda buat di sini...",
    )

    st.divider()

    # 2. Negative Prompt
    negative_prompt = st.text_input(
        "Negative Prompt (Elemen Dihindari)",
        value="blurry, low quality, distorted, bad anatomy",
        placeholder="Masukkan elemen yang ingin Anda hindari di sini...",
    )

    st.divider()

    # 3. Parameter Generasi
    col1, col2 = st.columns(2)
    with col1:
        scheduler_name = st.selectbox(
            "Noise Scheduler (Sampler)",
            options=[
                "DPMSolverMultistep",
                "EulerDiscrete",
                "EulerAncestralDiscrete",
                "DDIM",
                "LMSDiscrete",
            ],
            index=0,
        )
        guidance_scale = st.slider(
            "Skala CFG (Guidance Scale)",
            min_value=1.0,
            max_value=20.0,
            value=7.5,
            step=0.5,
        )

    with col2:
        num_inference_steps = st.slider(
            "Langkah Difusi (Inference Steps)",
            min_value=10,
            max_value=100,
            value=30,
            step=5,
        )
        seed_input = st.number_input(
            "Seed Integer (-1 untuk Acak)",
            value=-1,
            step=1,
        )
        batch_size = st.slider("Jumlah Gambar (Ukuran Batch)", min_value=1, max_value=4, value=1, step=1)

    # 4. Tombol Hasilkan Gambar
    btn_generate = st.button("🚀 Hasilkan Gambar AI", use_container_width=True, type="primary")

    st.divider()

    # 5. Tampilan Hasil Gambar Generasi
    st.subheader("Gambar Hasil Generasi")

    if btn_generate:
        if not prompt.strip():
            st.warning("Silakan masukkan prompt teks terlebih dahulu.")
        else:
            with st.spinner("Sedang menghasilkan gambar dengan Stable Diffusion 1.5..."):
                try:
                    service = get_service_instance()
                    final_seed = None if seed_input == -1 else int(seed_input)

                    if batch_size == 1:
                        result_img = service.generate_image(
                            prompt=prompt,
                            negative_prompt=negative_prompt,
                            scheduler_name=scheduler_name,
                            guidance_scale=guidance_scale,
                            num_inference_steps=num_inference_steps,
                            seed=final_seed,
                        )
                        st.session_state["generated_images"] = [result_img]
                        st.session_state["current_image"] = result_img
                    else:
                        batch_imgs, _ = service.generate_batch_images(
                            prompt=prompt,
                            batch_size=batch_size,
                            negative_prompt=negative_prompt,
                            save_outputs=True,
                        )
                        st.session_state["generated_images"] = batch_imgs
                        st.session_state["current_image"] = batch_imgs[0]

                    st.success("Proses Generasi Gambar Selesai!")
                except Exception as e:
                    st.error(f"Gagal menghasilkan gambar: {e}")

    # Tampilkan Gambar dalam Galeri
    if st.session_state["generated_images"]:
        imgs = st.session_state["generated_images"]
        if len(imgs) == 1:
            st.image(imgs[0], use_container_width=True, caption="Gambar Utama Hasil Sintesis")
            buf = io.BytesIO()
            imgs[0].save(buf, format="PNG")
            st.download_button(
                label="💾 Unduh Gambar PNG",
                data=buf.getvalue(),
                file_name="canvasgen_output.png",
                mime="image/png",
                use_container_width=True,
            )
        else:
            cols = st.columns(2)
            for idx, img in enumerate(imgs):
                with cols[idx % 2]:
                    st.image(img, use_container_width=True, caption=f"Sampel Batch #{idx+1}")
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button(
                        label=f"💾 Unduh Sampel #{idx+1}",
                        data=buf.getvalue(),
                        file_name=f"canvasgen_batch_{idx+1}.png",
                        mime="image/png",
                        key=f"dl_btn_{idx}",
                    )
    else:
        st.info("Gambar hasil generasi Anda akan ditampilkan di sini setelah Anda mengklik tombol 'Hasilkan Gambar AI'.")

# ==============================================================================
# MODE 2: PENGEDITAN GAMBAR (INPAINT & OUTPAINT)
# ==============================================================================
elif mode_selection == "🖼️ Pengeditan Gambar (Inpaint & Outpaint)":
    st.markdown('<div class="title-text">Pengeditan Gambar AI</div>', unsafe_allow_html=True)
    edit_type = st.radio("Mode Pengeditan", ["Inpainting (Pengeditan Bermasker)", "Outpainting (Ekspansi Kanvas)", "Zoom Out (Perbesar Kanvas)"], horizontal=True)

    source_option = st.radio("Sumber Gambar", ["Gunakan Gambar Generasi Terakhir", "Unggah Gambar Baru"], horizontal=True)
    base_image: Optional[Image.Image] = None

    if source_option == "Gunakan Gambar Generasi Terakhir":
        if st.session_state["current_image"]:
            base_image = st.session_state["current_image"]
            st.image(base_image, caption="Gambar Sumber (Generasi)", use_container_width=True)
        else:
            st.warning("Belum ada gambar generasi. Buat gambar terlebih dahulu di mode generator atau unggah gambar baru.")
    else:
        uploaded_file = st.file_uploader("Unggah Gambar (PNG/JPG)", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            base_image = Image.open(uploaded_file).convert("RGB")
            st.image(base_image, caption="Gambar Diunggah", use_container_width=True)

    edit_prompt = st.text_input("Prompt Pengeditan / Ekstensi Area", value="Bunga teratai mekar indah di atas air")

    if edit_type == "Inpainting (Pengeditan Bermasker)":
        mask_size = st.slider("Ukuran Area Masker Tengah (Piksel)", 50, 300, 150)
        btn_edit = st.button("🎨 Jalankan Inpainting", use_container_width=True, type="primary")
    elif edit_type == "Outpainting (Ekspansi Kanvas)":
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            pad_l = st.number_input("Batas Kiri", 0, 200, 50)
        with c2:
            pad_t = st.number_input("Batas Atas", 0, 200, 50)
        with c3:
            pad_r = st.number_input("Batas Kanan", 0, 200, 50)
        with c4:
            pad_b = st.number_input("Batas Bawah", 0, 200, 50)
        btn_edit = st.button("📐 Jalankan Outpainting", use_container_width=True, type="primary")
    else:
        zoom_factor = st.slider("Faktor Skala Zoom Out", 1.2, 2.0, 1.5, 0.1)
        btn_edit = st.button("🔍 Jalankan Zoom Out", use_container_width=True, type="primary")

    if btn_edit:
        if base_image is None:
            st.error("Silakan tentukan gambar sumber terlebih dahulu.")
        else:
            with st.spinner("Sedang memproses pengeditan gambar AI..."):
                try:
                    service = get_service_instance()
                    if edit_type == "Inpainting (Pengeditan Bermasker)":
                        w, h = base_image.size
                        mask = Image.new("L", (w, h), 0)
                        draw = ImageDraw.Draw(mask)
                        l = max(0, (w - mask_size) // 2)
                        t = max(0, (h - mask_size) // 2)
                        r = min(w, l + mask_size)
                        b = min(h, t + mask_size)
                        draw.rectangle([l, t, r, b], fill=255)

                        res_img, _ = service.inpaint_image(image=base_image, mask_image=mask, prompt=edit_prompt)
                    elif edit_type == "Outpainting (Ekspansi Kanvas)":
                        res_img, _ = service.outpaint_image(
                            image=base_image, padding=(pad_l, pad_t, pad_r, pad_b), prompt=edit_prompt
                        )
                    else:
                        res_img, _ = service.zoom_out_image(
                            image=base_image, zoom_factor=zoom_factor, prompt=edit_prompt
                        )

                    st.subheader("Gambar Hasil Pengeditan AI")
                    st.image(res_img, use_container_width=True)
                    buf = io.BytesIO()
                    res_img.save(buf, format="PNG")
                    st.download_button(
                        label="💾 Unduh Gambar Hasil Edit",
                        data=buf.getvalue(),
                        file_name="canvasgen_edited.png",
                        mime="image/png",
                        use_container_width=True,
                    )
                    st.success("Pengeditan Gambar Selesai!")
                except Exception as e:
                    st.error(f"Gagal memproses pengeditan: {e}")

# ==============================================================================
# MODE 3: PENGATURAN SISTEM
# ==============================================================================
else:
    st.markdown('<div class="title-text">Pengaturan Sistem & Hardware</div>', unsafe_allow_html=True)
    st.text_input("ID Model Diffusers", value="runwayml/stable-diffusion-v1-5", disabled=True)
    st.selectbox("Presisi Tipe Data (Precision)", ["fp16", "fp32", "bf16"], index=0)
    st.checkbox("Aktifkan Safety Checker", value=True)

    st.subheader("Diagnosa Memori & Hardware Sistem")
    st.json(get_vram_usage())
