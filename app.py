import streamlit as st
from groq import Groq

# --- Setup klien ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- Konfigurasi model ---
MODEL_UTAMA = "openai/gpt-oss-120b"
MODEL_CADANGAN = "openai/gpt-oss-20b"
MAX_HISTORY = 10  # batasi 10 pesan terakhir biar nggak kena token limit

SYSTEM_PROMPT = """Kamu adalah TanyaKampus AI, asisten virtual untuk mahasiswa 
Universitas Negeri Makassar. Jawab dengan ramah, singkat (maksimal 3-4 kalimat), 
dan dalam Bahasa Indonesia. Kalau ditanya di luar topik kampus, beasiswa, atau 
kehidupan mahasiswa, arahkan kembali dengan sopan."""

# --- UI ---
st.title("🎓 TanyaKampus AI")
st.caption("Chatbot buatan sendiri. Dibuat oleh peserta Study Jam AI/ML GDGoC UNM.")

# --- Inisialisasi riwayat chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Tampilkan semua pesan sebelumnya ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Input dari user ---
if prompt := st.chat_input("Tanya apa saja soal kampus..."):
    # Tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Siapkan payload untuk Groq
    with st.chat_message("assistant"):
        # Bangun messages: system prompt + history (dibatasi) + pesan terbaru
        payload = [{"role": "system", "content": SYSTEM_PROMPT}]
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