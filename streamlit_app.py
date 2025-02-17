import streamlit as st
import time
import replicate

DEFAULT_PRE_PROMT = "You are an expert audio guide content creator and great story teller."
DEFAULT_POST_PROMPT = "Do not include any formatting in your answer. Keep it short. Less than 1 min speech time."

REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
REPLICATE_MODEL_DEEPSEEK = st.secrets["REPLICATE_MODEL_DEEPSEEK"]

busy = False

st.title("🎈 Audio Guide")
st.subheader(" Content Creator Assistant")
st.text_input("Guide")
st.text_input("Point of Interest")

st.write(REPLICATE_API_TOKEN)
st.write(REPLICATE_MODEL_DEEPSEEK)

st.text_area("Pre-Prompt", DEFAULT_PRE_PROMT)
prompt = st.text_area("Prompt", "Type your prompt here")
st.text_area("Post-Prompt", DEFAULT_POST_PROMPT)

def submit_clicked():
    st.session_state.clicked = True
    busy = True
    input = { "prompt": prompt}
    output = replicate.run("deepseek-ai/deepseek-r1", input=input)
    st.write(output)

st.button("Submit", on_click=submit_clicked)

with st.expander("Processing", expanded=not busy):
    with st.spinner("Wait for it...", show_time=True):
        time.sleep(5)
    st.success("Done!")
    st.text_area("Response")