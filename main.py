import openai
import streamlit as st
import logging
import prompts
from llmchain import get_chain, create_prompt_template
from io import StringIO

if 'custom_system_prompt' not in st.session_state:
    st.session_state['custom_system_prompt'] = prompts.projektmanager

prompts = {'Vorstandsvorsitzender': prompts.vorstandsvorsitzender,
           'Projektmanager': prompts.projektmanager,
           'Controller': prompts.controller,
           'Energieberater': prompts.energieberater,
           'Ingenieur': prompts.ingenieur,
           'Benutzerdefiniert': st.session_state['custom_system_prompt']}

models = {'GPT 3.5 Turbo':"gpt-3.5-turbo",
          'GPT-4 (langsamer)':"gpt-4"}

def generate_response_test(prompt, model):
    """Generate a test response."""
    return "Hallo hier spricht die *AI* mit `code`"

def setup_session_state():
    """Initialize session state variables."""
    if 'max_token' not in st.session_state:
        st.session_state['max_token'] = 1000
    if 'temperature' not in st.session_state:
        st.session_state['temperature'] = 0.5
    if 'model' not in st.session_state:
        st.session_state['model'] = "gpt-3.5-turbo"
    if 'prompt_choice' not in st.session_state:
        st.session_state['prompt_choice'] = 'Projektmanager'
    if 'chain' not in st.session_state:
        st.session_state['chain'] = get_chain(st.session_state['model'],
                                              st.session_state['temperature'],
                                              st.session_state['max_token'],
                                              prompts[st.session_state['prompt_choice']],
                                              memory=None)
    if 'chat_text' not in st.session_state:
        st.session_state['chat_text'] = ""
    if 'user_input' not in st.session_state:
        st.session_state['user_input'] = ""

def chg_model_callback():
    st.session_state['chain'].llm.model_name=st.session_state['model']
        
def chg_prompt_callback():
    """Update the prompt based on the user's selection."""
    if st.session_state['prompt_choice'] != 'Benutzerdefiniert':
        st.session_state['chain'].prompt = create_prompt_template(prompts[st.session_state['prompt_choice']])

def update_chat_history(chat_history):
    """Update the chat history markdown."""
    chat_history.markdown(st.session_state['chat_text'], unsafe_allow_html=False)

def reset_callback():
    """Reset the chat session."""
    st.session_state['chat_text'] = ""
    st.session_state['user_input'] = ""
    st.session_state['chain'].memory.chat_memory.messages = []
    update_chat_history(chat_history)

def system_prompt_edit_callback():
    """Update the system prompt."""
    st.session_state['chain'].prompt = create_prompt_template(st.session_state['system_prompt_edit'])
    st.session_state['custom_system_prompt'] = st.session_state['system_prompt_edit']
    st.session_state['prompt_choice'] = "Benutzerdefiniert"

def text_area_callback(spinner_placeholder):
    """Handle user input and generate AI response."""
    st.session_state['chat_text'] += f"**You:**\n {st.session_state.user_input}\n\n"

    #with spinner_placeholder.spinner("Die KI generiert eine Antwort, bitte habe etwas Geduld..."):
    spinner_placeholder.markdown('<i class="fas fa-spinner fa-spin"></i> Die KI generiert eine Antwort...', 
                                 unsafe_allow_html=True)
    ai_response = st.session_state['chain'].predict(input=st.session_state.user_input)
    spinner_placeholder.markdown("", unsafe_allow_html=True)
    st.session_state['chat_text'] += f"**AI ({st.session_state['model']}):**\n {ai_response}\n\n"

# Streamlit App

#st.image("ai_app_logo.jpg", width=400)
#left_co, cent_co,last_co = st.columns(3)
#with cent_co:
#    st.image("ai_app_logo.jpg", width=400)

with st.columns(3)[1]:
    st.image("ai_app_logo.png")

st.title("FKM GPT Demo")

# Add space between title and chat history
#st.markdown("<h1 style='text-align: center; color: red;'>Some title</h1>", unsafe_allow_html=True)
#st.markdown("<style>img{text-align: center}</style>", unsafe_allow_html=True)
st.markdown("<style>h1{margin-bottom: 5px;text-align: center}</style>", unsafe_allow_html=True)
# Make chat history scrollable
st.markdown("<style>div[data-baseweb='select']{margin-top: 30px;}</style>", unsafe_allow_html=True)

setup_session_state()

left_co, right_co = st.columns(2)
with left_co:
    st.selectbox("Prompt Auswahl:", list(prompts.keys()), key='prompt_choice', on_change=chg_prompt_callback)
with right_co:
    st.selectbox("Modell Auswahl:", list(models.keys()), key='model', on_change=chg_model_callback)

    
with st.form("system_prompt_edit", clear_on_submit=False):
    st.text_area("System Prompt (muss nicht bearbeitet werden)", key='system_prompt_edit', 
                 value=prompts[st.session_state['prompt_choice']])
    st.form_submit_button('Systemprompt ändern (optional)', on_click=system_prompt_edit_callback)

chat_history = st.empty()
spinner_placeholder = st.empty()
update_chat_history(chat_history)

with st.form("chat_window", clear_on_submit=True):
    st.text_area("Geben Sie Ihre Nachricht ein:", key='user_input')
    st.form_submit_button('Abschicken', on_click=lambda: text_area_callback(spinner_placeholder))

st.button('Reset Chat', on_click=reset_callback)

st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" integrity="sha512-iecdLmaskl7CVkqkXNQ/ZH/XLlvWZOJyj7Yy7tcenmpD1ypASozpmT/E0iPtmFIB46ZmdtAc9eNBvH0H/ZpiBw==" crossorigin="anonymous" referrerpolicy="no-referrer" />', unsafe_allow_html=True)
