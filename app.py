import streamlit as st
import google.generativeai as genai
import os
import time
from io import BytesIO

# Membaca pustaka pembaca PDF opsional (aman jika belum diinstal)
try:
    import pypdf
    PDF_READER_AVAILABLE = True
except ImportError:
    PDF_READER_AVAILABLE = False

# =====================================================================
# 1. KONFIGURASI HALAMAN & DESIGN SYSTEM (CSS)
# =====================================================================
st.set_page_config(
    page_title="MathBuddy PjBL - Asisten Guru Matematika SD",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS untuk menyesuaikan tema pendidikan & kemudahan baca
st.markdown("""
<style>
    /* Styling Umum */
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .badge-research {
        background-color: #E0F2FE;
        color: #0369A1;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
    }
    /* Kotak Informasi Proyek */
    .project-card {
        background-color: #F8FAFC;
        border-left: 5px solid #3B82F6;
        padding: 1.2rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .project-title {
        font-weight: 700;
        color: #1E293B;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. STATUS PERCAKAPAN & MEMORI (SESSION STATE)
# =====================================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo Bapak/Ibu Guru Hebat! 👋 Saya **MathBuddy-PjBL**, asisten AI yang dirancang khusus untuk membantu Anda mengimplementasikan model pembelajaran berbasis proyek (PjBL) guna meruntuhkan keabstrakan konsep matematika SD. \n\nSilakan pilih topik di bilah samping atau tanyakan ide proyek matematika di sini!"}
    ]
if "pdf_context" not in st.session_state:
    st.session_state.pdf_context = ""

# =====================================================================
# 3. INTERFACE INTEGRASI GEMINI DENGAN EXPONENTIAL BACKOFF
# =====================================================================
def generate_gemini_response(prompt, system_instruction, api_key, context=""):
    """Mengirim permintaan ke Gemini API dengan penanganan kesalahan dan percobaan ulang."""
    if not api_key:
        return "⚠️ Silakan masukkan **Gemini API Key** Anda di sidebar untuk mengaktifkan kecerdasan AI."
    
    try:
        genai.configure(api_key=api_key)
        # Menggunakan model standar yang disarankan lingkungan
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "temperature": 0.3, # Diatur rendah agar konten matematika tetap akurat secara ilmiah
                "top_p": 0.95,
                "top_k": 40,
            }
        )
        
        # Gabungkan konteks PDF jika tersedia
        full_prompt = prompt
        if context:
            full_prompt = f"Gunakan informasi dari dokumen kurikulum/buku teks berikut untuk membantu merumuskan jawaban.\n\nKonteks Dokumen:\n{context}\n\nPertanyaan/Instruksi Guru:\n{prompt}"
            
        # Inisialisasi percakapan dengan System Instruction
        chat = model.start_chat(history=[])
        
        # Exponential backoff retry logic (Hingga 5 kali)
        for attempt in range(5):
            try:
                response = chat.send_message(
                    f"[SYSTEM INSTRUCTION]: {system_instruction}\n\n[USER INPUT]: {full_prompt}"
                )
                return response.text
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    sleep_time = 2 ** attempt
                    time.sleep(sleep_time)
                else:
                    raise e
        return "⚠️ Maaf, server sedang sibuk. Silakan coba kirim pesan Anda kembali."
    except Exception as e:
        return f"❌ Terjadi kesalahan pada API Gemini: {str(e)}"

# =====================================================================
# 4. KONTEN SIDEBAR (KONFIGURASI PARAMETER & FILE DATABASE)
# =====================================================================
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=300&q=80", caption="AI-Supported Learning Tool", use_container_width=True)
    st.title("⚙️ Konfigurasi MathBuddy")
    
    # Kunci API
    api_key_input = st.text_input("1. Masukkan Gemini API Key:", type="password", help="Dapatkan kunci API Anda secara gratis di Google AI Studio.")
    
    st.markdown("---")
    st.subheader("🎒 Database Kurikulum & Materi")
    
    # Fitur Unggah Buku Materi (Simulasi Database PDF)
    uploaded_file = st.file_uploader("Unggah Buku Materi SD (PDF)", type=["pdf"])
    if uploaded_file is not None:
        if PDF_READER_AVAILABLE:
            with st.spinner("Sedang mengekstrak materi buku matematika... 📖"):
                try:
                    pdf_reader = pypdf.PdfReader(BytesIO(uploaded_file.read()))
                    extracted_text = ""
                    # Membatasi ekstraksi 15 halaman pertama demi efisiensi token
                    num_pages = min(len(pdf_reader.pages), 15)
                    for i in range(num_pages):
                        extracted_text += pdf_reader.pages[i].extract_text() + "\n"
                    st.session_state.pdf_context = extracted_text
                    st.success(f"✅ Berhasil memproses {num_pages} halaman buku!")
                except Exception as e:
                    st.error(f"Gagal membaca PDF: {e}")
        else:
            st.warning("Pustaka 'pypdf' tidak terpasang. Menjalankan mode simulasi berbasis teks.")
            st.session_state.pdf_context = "Simulasi buku teks Matematika SD Kelas 4 Bab Pecahan dan Geometri Bangun Ruang."

    st.markdown("---")
    st.subheader("🏫 Parameter PjBL")
    
    # Dropdown kelas dasar
    kelas_selected = st.selectbox(
        "Pilih Kelas:",
        ["Kelas 1 (Fase A)", "Kelas 2 (Fase A)", "Kelas 3 (Fase B)", "Kelas 4 (Fase B)", "Kelas 5 (Fase C)", "Kelas 6 (Fase C)"]
    )
    
    # Dropdown materi abstrak matematika SD
    topik_abstrak = st.selectbox(
        "Topik Matematika Abstrak:",
        [
            "Konsep Pecahan (Bagian dari Keseluruhan)",
            "Nilai Tempat Satuan, Puluhan, Ratusan",
            "Sifat Jaring-Jaring Bangun Ruang 3D",
            "Pembagian sebagai Pengurangan Berulang",
            "Pengukuran Sudut dan Estimasi",
            "Pengolahan Data (Diagram & Grafik)"
        ]
    )
    
    # Pilihan template proyek siap pakai
    st.subheader("💡 Template Proyek Instan")
    generate_template = st.button("Rancang Proyek PjBL Instan")

# =====================================================================
# 5. AREA UTAMA: DESKRIPSI PENELITIAN & PERCAKAPAN CHAT
# =====================================================================
st.markdown('<div class="badge-research">🧬 MODEL PENELITIAN AKTIF: Generative AI-Supported PjBL di SD</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-header">MathBuddy-PjBL</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Membantu Guru memetakan materi abstrak sekolah dasar ke dalam petualangan proyek dunia nyata yang konkret dan bermakna.</p>', unsafe_allow_html=True)

# Petunjuk penggunaan singkat bagi Guru / Peneliti
with st.expander("ℹ️ Cara Kerja Sistem dalam Riset PjBL Anda", expanded=False):
    st.markdown("""
    Aplikasi ini bertindak sebagai **Scaffolding Tool (Alat Bantu Pendamping)** untuk guru dalam mendesain pembelajaran berbasis proyek. 
    Langkah yang disarankan untuk guru selama riset:
    1. **Tentukan Topik:** Pilih tingkatan kelas dan materi abstrak yang ingin diajarkan di bilah kiri.
    2. **Desain Sintaks:** Gunakan tombol **'Rancang Proyek PjBL Instan'** untuk mendapatkan perencanaan komprehensif berstandar Kurikulum Merdeka.
    3. **Konsultasikan Hambatan:** Tanyakan hambatan atau cara mengatasi miskonsepsi siswa langsung di kolom chat di bawah.
    """)

# SYSTEM INSTRUCTION UNTUK PROMPT REKAYASA (PROMPTING ENGINEERING)
system_prompt = f"""
Kamu adalah "MathBuddy-PjBL", seorang pakar kurikulum matematika SD, psikolog perkembangan anak, dan spesialis model pembelajaran Project-Based Learning (PjBL) di Indonesia.
Fokus utamamu adalah membantu Guru merancang aktivitas pembelajaran berbasis proyek yang mengubah konsep matematika abstrak menjadi pengalaman fisik yang nyata (konkret) bagi siswa SD.

Karakteristik Komunikasimu:
1. Menggunakan sapaan ramah dan mendukung seperti "Bapak/Ibu Guru yang hebat".
2. Gaya bahasa profesional, edukatif, inspiratif namun mudah dipahami.
3. Selalu membagi rancangan proyek ke dalam 6 langkah sintaks PjBL standar Indonesia:
   - Tahap 1: Pertanyaan Mendasar (Essential Question)
   - Tahap 2: Mendesain Perencanaan Proyek (Project Design)
   - Tahap 3: Menyusun Jadwal Pembuatan (Scheduling)
   - Tahap 4: Memonitor Keaktifan dan Perkembangan Proyek (Monitoring)
   - Tahap 5: Menguji Hasil / Presentasi (Assessing)
   - Tahap 6: Evaluasi Pengalaman Belajar (Reflection)
4. Pastikan proyek menggunakan bahan yang murah, mudah dicari di lingkungan sekitar anak (seperti kardus bekas, sedotan, botol plastik, atau kertas warna).
5. Tunjukkan bagaimana teknologi Generative AI dapat digunakan oleh guru atau siswa di kelas untuk mendukung pengerjaan proyek tersebut.
"""

# Pembuatan aksi instan dari tombol Template Proyek
if generate_template:
    tanya_template = f"Buatkan modul rancangan pembelajaran PjBL lengkap untuk {kelas_selected} dengan topik abstrak '{topik_abstrak}'. Jabarkan langkah-langkah konkret sesuai 6 sintaks PjBL, bahan fisik yang dibutuhkan siswa, serta bagaimana asisten AI ini mendukung proses pengerjaannya!"
    st.session_state.messages.append({"role": "user", "content": tanya_template})
    
    with st.spinner("Sedang merancang struktur proyek terbaik untuk Anda... 🛠️"):
        jawaban_ai = generate_gemini_response(
            prompt=tanya_template,
            system_instruction=system_prompt,
            api_key=api_key_input,
            context=st.session_state.pdf_context
        )
        st.session_state.messages.append({"role": "assistant", "content": jawaban_ai})

# Menampilkan Riwayat Obrolan Chat secara Responsif
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Kolom Input Chat Interaktif di Bagian Bawah
if prompt_user := st.chat_input("Tanyakan cara mengajarkan matematika abstrak, ide modul ajar, atau kembangkan proyek..."):
    # Masukkan pertanyaan user ke dalam history
    st.session_state.messages.append({"role": "user", "content": prompt_user})
    with st.chat_message("user"):
        st.markdown(prompt_user)
        
    # Generate respons dari AI
    with st.chat_message("assistant"):
        with st.spinner("Berpikir selaku Asisten PjBL... 🧠"):
            jawaban_ai = generate_gemini_response(
                prompt=prompt_user,
                system_instruction=system_prompt,
                api_key=api_key_input,
                context=st.session_state.pdf_context
            )
            st.markdown(jawaban_ai)
            st.session_state.messages.append({"role": "assistant", "content": jawaban_ai})

# Tombol untuk mereset riwayat diskusi demi fleksibilitas riset
st.markdown("<br><hr>", unsafe_allow_html=True)
if st.button("🔄 Atur Ulang Sesi Percakapan"):
    st.session_state.messages = [
        {"role": "assistant", "content": "Sesi telah diatur ulang. Silakan pilih topik di bilah samping atau tanyakan ide proyek matematika di sini!"}
    ]
    st.rerun()
