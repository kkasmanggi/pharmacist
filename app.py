import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# KONFIGURASI APLIKASI STREAMLIT
# ==============================================================================

st.set_page_config(
    page_title="🤖 Chatbot Apoteker",
    page_icon="💊",
    layout="centered"
)

# Judul dan deskripsi di UI
st.title("🤖 Chatbot Apoteker")
st.markdown("Halo! Saya adalah chatbot apoteker yang siap membantu Anda. Silakan tanyakan tentang obat yang Anda butuhkan.")

# ==============================================================================
# PENGATURAN API KEY DAN MODEL
# ==============================================================================

# Mengambil API Key dari Streamlit Secrets atau Environment Variables
# Ini adalah cara yang aman untuk menyimpan kredensial.
# JANGAN SIMPAN API KEY LANGSUNG DI KODE ANDA.
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    st.warning("GEMINI_API_KEY belum diatur di Streamlit Secrets. "
               "Silakan tambahkan di `Secrets` pada dashboard Streamlit Cloud Anda.")
    st.stop() # Hentikan aplikasi jika API Key tidak ada

MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

# Definisikan peran chatbot Anda di sini.
INITIAL_CHATBOT_CONTEXT = [
    {"role": "user", "parts": ["Saya adalah seorang apoteker. Tuliskan obat apa yang diinginkan untuk menyembuhkan penyakit Anda. Jawaban singkat dan jelas. Tolak pertanyaan selain tentang obat."]},
    {"role": "model", "parts": ["Baik! Saya akan menjawab pertanyaan Anda tentang obat."]}
]

# ==============================================================================
# FUNGSI UTAMA DAN LOGIKA STREAMLIT
# ==============================================================================

# Konfigurasi Gemini API
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"Kesalahan saat mengkonfigurasi API Key: {e}")
    st.stop()

# Inisialisasi model
@st.cache_resource
def get_model():
    """Menginisialisasi dan menyimpan model dalam cache untuk efisiensi."""
    return genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=500
        )
    )

model = get_model()

# Inisialisasi riwayat chat
if "messages" not in st.session_state:
    st.session_state.messages = INITIAL_CHATBOT_CONTEXT.copy()

# Tampilkan riwayat pesan yang ada
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["parts"][0])
    elif message["role"] == "model":
        with st.chat_message("assistant"):
            st.markdown(message["parts"][0])

# Menerima input dari pengguna
if prompt := st.chat_input("Tanyakan tentang obat..."):
    # Tambahkan pesan pengguna ke riwayat
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kirim input ke model dan dapatkan respons
    try:
        # Gunakan riwayat dari st.session_state
        chat_session = model.start_chat(history=st.session_state.messages)
        response = chat_session.send_message(prompt)

        # Tambahkan respons model ke riwayat
        st.session_state.messages.append({"role": "model", "parts": [response.text]})

        with st.chat_message("assistant"):
            st.markdown(response.text)

    except Exception as e:
        st.error("Maaf, terjadi kesalahan saat berkomunikasi dengan Gemini.")
        st.error(f"Detail kesalahan: {e}")
        st.warning("Kemungkinan penyebab: masalah koneksi, API key tidak valid, atau kuota habis.")


