import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# KONFIGURASI APLIKASI STREAMLIT
# ==============================================================================

# Mengatur tata letak halaman menjadi 'lebar' (wide)
st.set_page_config(layout="wide", page_title="Chatbot Apoteker")

# Judul utama aplikasi di sidebar
st.sidebar.title("🩺 Chatbot Apoteker 💊")
st.sidebar.markdown("---")

# ==============================================================================
# PENGATURAN API KEY DAN MODEL
# ==============================================================================

# Menggunakan Streamlit secrets untuk menyimpan API Key
# Ini adalah cara paling aman untuk deployment di GitHub
# Buat file .streamlit/secrets.toml di repository Anda dan tambahkan:
# GEMINI_API_KEY="AIzaSyBWzMBC6hVzvooktYrFkO5fvrDuJKVxqio"
# Atau, jika Anda menjalankan lokal, gunakan st.text_input
api_key = st.sidebar.text_input("Masukkan API Key Gemini Anda:", type="password")

if not api_key:
    st.info("⚠️ Harap masukkan API Key Gemini Anda untuk memulai.")
    st.stop()

# Mengatur API Key setelah diinput
try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"❌ Kesalahan konfigurasi API Key: {e}")
    st.stop()

# Menampilkan informasi model
model_name = 'gemini-1.5-flash'
st.sidebar.markdown(f"**Model yang Digunakan:** `{model_name}`")

# ==============================================================================
# FUNGSI UNTUK MEMBUAT CHAT DAN MENGIRIM PESAN
# ==============================================================================

@st.cache_resource(show_spinner="Menyiapkan model...")
def get_model():
    """Menginisialisasi dan mengembalikan model Gemini."""
    try:
        return genai.GenerativeModel(
            model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                max_output_tokens=500
            )
        )
    except Exception as e:
        st.error(f"❌ Kesalahan saat inisialisasi model: {e}")
        st.stop()

def initialize_chat():
    """Menginisialisasi sesi chat dengan riwayat awal."""
    # Definisikan peran chatbot
    initial_context = [
        {"role": "user", "parts": ["Saya adalah seorang apoteker. Tuliskan obat apa yang di inginkan untuk menyembuhkan penyakit Anda. Jawaban singkat dan jelas. Tolak pertanyaan selain tentang obat."]},
        {"role": "model", "parts": ["Baik! Saya akan menjawab pertanyaan Anda tentang Obat."]}
    ]
    model = get_model()
    return model.start_chat(history=initial_context)

# ==============================================================================
# APLIKASI UTAMA STREAMLIT
# ==============================================================================

st.header("Selamat Datang di Chatbot Apoteker! 💊", divider="blue")
st.markdown("Tanyakan kepada saya tentang obat yang Anda butuhkan, dan saya akan memberikan informasi singkat dan jelas. 👋")

# Inisialisasi chat di session state jika belum ada
if "chat_session" not in st.session_state:
    st.session_state.chat_session = initialize_chat()

# Menampilkan riwayat chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Menambahkan pesan pembuka dari model ke riwayat
if not st.session_state.messages:
    # Ambil pesan awal dari inisialisasi chat
    initial_message = st.session_state.chat_session.history[1].parts[0].text
    st.session_state.messages.append({"role": "assistant", "content": initial_message})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kolom input untuk pengguna
if prompt := st.chat_input("Apa nama obat untuk penyakit Anda?"):
    # Tambahkan pesan pengguna ke riwayat dan tampilkan
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kirim prompt ke Gemini dan tampilkan balasan
    with st.chat_message("assistant"):
        with st.spinner("Sedang mencari informasi..."):
            try:
                response = st.session_state.chat_session.send_message(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"❌ Maaf, terjadi kesalahan saat memproses permintaan Anda: {e}")

# Tombol untuk mereset chat
if st.sidebar.button("Mulai Chat Baru"):
    st.session_state.messages = []
    st.session_state.chat_session = initialize_chat()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("Disclaimer: Informasi ini hanya sebagai panduan awal. Selalu konsultasikan dengan apoteker atau dokter profesional untuk diagnosis dan pengobatan yang tepat.")
