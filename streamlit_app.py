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

# Inputs
pre = st.text_area("Pre-Prompt", DEFAULT_PRE_PROMT)
include_pre = st.toggle("Include pre-prompt", True)

prompt = st.text_area("Prompt", SAMPLE_PROMPT)

post = st.text_area("Post-Prompt", DEFAULT_POST_PROMPT)
include_post = st.toggle("Include post-prompt", True)

# Assemble final prompt
final_prompt = ""
if (include_pre):
    final_prompt = pre + " "
final_prompt = final_prompt + prompt + " "
if (include_post):
    final_prompt = final_prompt + post

input = { "prompt": final_prompt}

final = st.text_area("Final-Prompt", final_prompt)

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

    # Move the element with </think> to the response if it has leading or lagging characters
    if "</think>" in thinking_str:
        end_index = thinking_str.find("</think>")
        thinking_str = thinking_str[:end_index].strip()
        response_str = thinking_str[end_index + len("</think>"):].strip() + response_str

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