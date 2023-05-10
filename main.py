import openai
import streamlit as st
import logging
#import streamlit_scrollable_textbox as stx
import prompts
from llmchain import get_chain, create_prompt_template
from io import StringIO

if 'custom_system_prompt' not in st.session_state:
    st.session_state['custom_system_prompt'] = prompts.assistant

prompts={'Assistant': prompts.assistant,
         'Code':prompts.python,
         'Berater': prompts.consultant,
         'Prompt Builder':prompts.prompt_builder,
         'Übersetzer': prompts.uebersetzer,
         'Benutzerdefiniert': st.session_state['custom_system_prompt']}

# Define function to generate AI response
def generate_response_test(prompt, model):
    return "Hallo hier spricht die *AI* mit `code`"
  
# Streamlit App

st.title("SWD FKM GPT Demo")
# Add space between title and chat history
st.markdown("<style>h1{margin-bottom: 15px;}</style>", unsafe_allow_html=True)
# Make chat history scrollable
st.markdown("<style>div[data-baseweb='select']{margin-top: 30px;}</style>", unsafe_allow_html=True)

if 'max_token' not in st.session_state:
    st.session_state['max_token']=1000
if 'temperature' not in st.session_state:
    st.session_state['temperature']=0.5
if 'model' not in st.session_state:
    st.session_state['model']="gpt-3.5-turbo"
if 'prompt_choice' not in st.session_state:
    st.session_state['prompt_choice']='Assistant'

if 'chain' not in st.session_state:
    st.session_state['chain'] = get_chain(st.session_state['model'],
                                          st.session_state['temperature'],
                                          st.session_state['max_token'],
                                          prompts[st.session_state['prompt_choice']],
                                          memory=None)

def chg_prompt_callback():
    if st.session_state['prompt_choice']!='Benutzerdefiniert':
        st.session_state['chain'].prompt=create_prompt_template(prompts[st.session_state['prompt_choice']])

st.selectbox("Prompt:", list(prompts.keys()), key='prompt_choice', on_change=chg_prompt_callback)




if 'chat_text' not in st.session_state:
    st.session_state['chat_text'] = ""
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = ""


def update_chat_history():
    chat_history.markdown(st.session_state['chat_text'], unsafe_allow_html=False)

def reset_callback():
    st.session_state['chat_text'] = ""
    st.session_state['user_input'] = ""
    st.session_state['chain'].memory.chat_memory.messages=[]
    update_chat_history()

def system_prompt_edit_callback():
    st.session_state['chain'].prompt=create_prompt_template(st.session_state['system_prompt_edit'])
    st.session_state['custom_system_prompt']=st.session_state['system_prompt_edit']
    st.session_state['prompt_choice']="Benutzerdefiniert"

with st.form("system_prompt_edit", clear_on_submit=False):
    st.text_area("System Prompt", key='system_prompt_edit', 
                 value=prompts[st.session_state['prompt_choice']])
    st.form_submit_button('Submit', on_click=system_prompt_edit_callback)

def text_area_callback():
    st.session_state['chat_text']+= f"**You:**\n {st.session_state.user_input}\n\n" 
    ai_response = st.session_state['chain'].predict(input=st.session_state.user_input)
    st.session_state['chat_text']+= f"**AI ({st.session_state['model']}):**\n {ai_response}\n\n"

with st.form("chat_window", clear_on_submit=True):
    st.text_area("Type your message:", key='user_input')
    st.form_submit_button('Submit', on_click=text_area_callback)

chat_history = st.empty()
update_chat_history()

st.button('Reset Chat', on_click=reset_callback)
