import streamlit as st
import time
import replicate
from st_supabase_connection import SupabaseConnection, execute_query

DEFAULT_PRE_PROMT = ("You are an expert audio guide content creator "
                     "and great story teller.")
DEFAULT_POST_PROMPT = ("Do not include any formatting in your answer. "
                       "I will use it for text to speech. "
                       "Keep it short and sweet, than 1 min speech time.")

REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
REPLICATE_MODEL_DEEPSEEK = st.secrets["REPLICATE_MODEL_DEEPSEEK"]
REPLICATE_MODEL_KOKORO = "jaaari/kokoro-82m:f559560eb822dc509045f3921a1921234918b91739db4bf3daab2169b71c7a13"
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_ANON_KEY = st.secrets["SUPABASE_ANON_KEY"]

st_supabase_client = st.connection(
    name="supabase_connection",
    type=SupabaseConnection,
    ttl=None,
    url=SUPABASE_URL,
    key=SUPABASE_ANON_KEY,
)

voices = execute_query(st_supabase_client.table(
    "kokoro_voices").select("*"), ttl=0)
# st.write(voices)

unique_lang_codes = list({item["lang_code"] for item in voices.data})
# st.write(unique_lang_codes)

languages = execute_query(
    st_supabase_client.table("language").select("*"), ttl=0)
unique_languages = {item["code"]: item["name"] for item in languages.data}
# st.write(languages)
# st.write(unique_languages)


def language_format_func(option):
    return unique_languages[option]


gender_lookup = {"m": "Male", "f": "Female"}


def gender_format_func(option):
    return gender_lookup[option]


def filter_and_format_voices(lang_code, gender):
    return [{"lang_code": voice["lang_code"], "name": voice["name"], "gender": voice["gender"]} for voice in voices.data if voice["lang_code"] == lang_code and voice["gender"] == gender]


def format_name(voice):
    return voice["name"].split('_', 1)[1]


if "last_narrative" not in st.session_state:
    st.session_state["last_narrative"] = ""

# st.write(st.session_state)

st.title("🎈 Audio Guide")
st.subheader(" Content Creator Assistant")
guide = st.text_input("Guide", "Ganga Talao")
poi = st.text_input("Point of Interest", "Durga")

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

voice_input = {"prompt": final_prompt}

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
        response_str = thinking_str[end_index +
                                    len("</think>"):].strip() + response_str

    return thinking_str, response_str


if st.button("Generate Narrative for: " + guide + "," + poi):
    with st.spinner('Generating Narrative…'):
        start_time = time.time()
        output = replicate.run(REPLICATE_MODEL_DEEPSEEK, input=voice_input)
        end_time = time.time()
        elapsed_time = end_time - start_time
        st.write(f"Narrative generated in {elapsed_time:.2f} seconds")
        # st.write(output)
        thinking, response = split_thinking_response(output)
        st.text_area("Thinking", thinking)
        st.text_area("Response", response)
        st.session_state["last_narrative"] = response
        # st.text_area("last_narrative", st.session_state.last_narrative)

selected_language = st.selectbox(
    "Languages", unique_languages, format_func=language_format_func)
st.write("selected_language",selected_language)

selected_gender = st.selectbox("Gender", options=list(
    gender_lookup.keys()), format_func=gender_format_func)
st.write("selected_gender",selected_gender)

filtered_voices = filter_and_format_voices(
    selected_language, selected_gender)
st.write("filtered_voices",filtered_voices)

selected_voice = st.selectbox(
    "Voice", options=filtered_voices, format_func=format_name)
st.write("selected_voice",selected_voice)

if st.button("Generate Voice for: " + guide + "," + poi, disabled=len(st.session_state["last_narrative"]) == 0 or selected_language is None or selected_gender is None or selected_voice is None):
    with st.spinner('Generating Voice'):
        start_time = time.time()
        voice_input = {
            "text": st.session_state["last_narrative"],
            "voice": selected_voice["name"],
            "stream": "false"
        }
        st.write(voice_input)
        output = replicate.run(
            REPLICATE_MODEL_KOKORO,
            input=voice_input,
            # Note: Make sure this is False otherwise you get a file
            #       that st.audio cannot handle.
            #       With this false you get a url back from replicate/kokoro
            use_file_output=False
        )
        end_time = time.time()
        elapsed_time = end_time - start_time
        st.write(f"Voice generated in {elapsed_time:.2f} seconds")
        st.write(output)
        st.audio(output, format="audio/wav")
