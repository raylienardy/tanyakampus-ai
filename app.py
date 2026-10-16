# ============================================================
# TanyaKampus AI - Showcase GDGoC UNM 2026/2027
# Author: Raynato Lienardy
# ============================================================

import streamlit as st
from groq import Groq

# --- 1. Konfigurasi halaman (WAJIB paling atas) ---
st.set_page_config(
    page_title="TanyaKampus AI",
    page_icon="🎓",
    layout="centered",
)

# --- 2. CSS Custom (Level 1: kosmetik) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main .block-container {
        background: rgba(255, 255, 255, 0.96);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        margin-top: 1.5rem;
    }
    
    h1 {
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    .stChatMessage {
        animation: fadeIn 0.4s ease-in;
        border-radius: 12px;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.98);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Setup klien Groq ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 4. Konfigurasi model ---
MODEL_UTAMA = "openai/gpt-oss-120b"
MODEL_CADANGAN = "openai/gpt-oss-20b"
MAX_HISTORY = 10  # batasi 10 pesan terakhir biar nggak kena token limit

# --- 5. Definisi persona (Level 2) ---
PERSONAS = {
    "🎓 Asisten Akademik": """Kamu adalah TanyaKampus AI, asisten akademik untuk mahasiswa 
Universitas Negeri Makassar. Jawab dengan ramah, singkat (3-4 kalimat), dan informatif. 
Fokus pada topik kampus, beasiswa, akademik, dan kehidupan mahasiswa. 
Kalau di luar topik itu, arahkan kembali dengan sopan.""",

    "💙 Teman Curhat": """Kamu adalah teman curhat yang empatik untuk mahasiswa. 
Dengerin keluh kesah mereka dengan hangat, validasi perasaan mereka, dan kasih saran 
praktis kalau diminta. Jawab dengan bahasa santai, akrab, dan penuh empati. 
Maksimal 4 kalimat. Jangan menghakimi.""",

    "🎨 Generator Ide": """Kamu adalah brainstorming partner kreatif. Kalau user kasih 
topik, kasih 3 ide segar yang out-of-the-box dalam format bullet. 
Setiap ide 1 kalimat. Selalu tanya balik: 'Mau aku kembangkan yang mana?'""",

    "😂 Stand-up Comedian": """Kamu adalah komedian yang lucu dan sopan. 
Jawab setiap pertanyaan dengan punchline ringan, tapi tetap ada isi. 
Maksimal 3 kalimat. Hindari humor yang menyinggung SARA atau fisik seseorang.""",
}

# --- 6. Sidebar: persona switcher + reset + saran ---
with st.sidebar:
    st.markdown("### 🎭 Pilih Mode")
    persona_pilihan = st.radio(
        "Kepribadian AI:",
        list(PERSONAS.keys()),
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 💡 Coba tanya:")
    st.markdown("""
    - *Apa beasiswa untuk mahasiswa UNM?*
    - *Aku capek kuliah, kasih semangat*
    - *Ide proyek AI untuk jurusan hukum*
    - *Ceritakan lelucon tentang mahasiswa*
    """)
    
    st.markdown("---")
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 7. Header ---
st.title("🎓 TanyaKampus AI")
st.caption("Chatbot buatan sendiri. Dibuat oleh peserta Study Jam AI/ML GDGoC UNM.")

# --- 8. Inisialisasi riwayat chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 9. Tampilkan semua pesan sebelumnya ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 10. Input dari user ---
if prompt := st.chat_input("Tanya apa saja soal kampus..."):
    # Tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Dapatkan respons dari Groq
    with st.chat_message("assistant"):
        # Bangun payload: system prompt (sesuai persona) + history
        payload = [{"role": "system", "content": PERSONAS[persona_pilihan]}]
        payload += st.session_state.messages[-MAX_HISTORY:]

        # Coba model utama, fallback ke cadangan kalau kena rate limit
        try:
            response = client.chat.completions.create(
                messages=payload,
                model=MODEL_UTAMA,
            )
        except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                st.warning("Model utama sibuk, pindah ke model cadangan...")
                response = client.chat.completions.create(
                    messages=payload,
                    model=MODEL_CADANGAN,
                )
            else:
                st.error(f"Error: {e}")
                st.stop()

        jawaban = response.choices[0].message.content
        st.markdown(jawaban)

    st.session_state.messages.append({"role": "assistant", "content": jawaban})
