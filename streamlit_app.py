import streamlit as st
import time
import replicate

DEFAULT_PRE_PROMT = ("You are an expert audio guide content creator "
                     "and great story teller.")
DEFAULT_POST_PROMPT = ("Do not include any formatting in your answer. "
                       "I will use it for text to speech. " 
                       "Keep it short and sweet, than 1 min speech time.")

REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
REPLICATE_MODEL_DEEPSEEK = st.secrets["REPLICATE_MODEL_DEEPSEEK"]

busy = False

st.title("🎈 Audio Guide")
st.subheader(" Content Creator Assistant")
guide = st.text_input("Guide", "Ganga Talao")
poi = st.text_input("Point of Interest", "Durga")

# st.write(REPLICATE_API_TOKEN)
# st.write(REPLICATE_MODEL_DEEPSEEK)

SAMPLE_PROMPT = ("Write the story for a magestic statue of Durga " 
                 "standing next to a large lion "
                 "at the indian sacred site of Ganga Talao next to a mysterious crator lake."
                 )

pre = st.text_area("Pre-Prompt", DEFAULT_PRE_PROMT)
prompt = st.text_area("Prompt", SAMPLE_PROMPT)
post = st.text_area("Post-Prompt", DEFAULT_POST_PROMPT)

final_prompt = pre + " " + prompt + " " + post
input = { "prompt": final_prompt}

# def submit_clicked():
#     st.session_state.clicked = True
#     busy = True
#     input = { "prompt": final_prompt}
#     output = replicate.run(REPLICATE_MODEL_DEEPSEEK, input=input)
#     st.write(output)

# st.button("Submit", on_click=submit_clicked)

# with st.expander("Processing", expanded=not busy):
#     with st.spinner("Wait for it...", show_time=True):
#         time.sleep(5)
#     st.success("Done!")
#     st.text_area("Response")

def split_thinking_response(data):
    thinking = []
    response = []
    in_thinking = False

    for element in data:
        if "<think>" in element:
            in_thinking = True
            thinking.append(element.replace("<think>", ""))
        elif "</think>" in element:
            in_thinking = False
            thinking.append(element.replace("</think>", ""))
        elif in_thinking:
            thinking.append(element)
        else:
            response.append(element)

    # Combine all thinking elements into a single string
    thinking_str = ''.join(thinking).strip()
    # Combine all response elements into a single string
    response_str = ''.join(response).strip()

    return thinking_str, response_str

if st.button("Generate Narrative for: " + guide + "," + poi ):
  with st.spinner('Generating Narrative…'):
    start_time = time.time()
    output = replicate.run( REPLICATE_MODEL_DEEPSEEK, input=input)
    end_time = time.time()
    elapsed_time = end_time - start_time
    st.write(f"Narrative generated in {elapsed_time:.2f} seconds")
    thinking, response = split_thinking_response(output)
    st.text_area("Thinking", thinking)
    st.text_area("Response", response)