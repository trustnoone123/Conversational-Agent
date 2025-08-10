import streamlit as st

def show_url_input():
    return st.text_input("🔗 Enter Flipkart Product or Listing URL:")

def show_summary(summary):
    st.subheader("📦 Summarized Product Info")
    st.json(summary)

def play_audio(audio_path):
    with open(audio_path, "rb") as f:
        st.audio(f.read(), format="audio/mp3")
