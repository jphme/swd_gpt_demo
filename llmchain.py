import os
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

def create_prompt_template(system_prompt):
    return ChatPromptTemplate.from_messages([SystemMessagePromptTemplate.from_template(system_prompt),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")])

def get_chain(modelname, temperature, max_token, system_prompt, memory=None):
    llm=ChatOpenAI(temperature=temperature,
                   max_tokens=max_token,
                   model=modelname, #'gpt-3.5-turbo'
                   openai_api_key=os.getenv("OPENAI_API_KEY")
                  )
    if memory is None:
        memory = ConversationBufferMemory(return_messages=True)
    prompt =create_prompt_template(system_prompt)
    return ConversationChain(memory=memory, prompt=prompt, llm=llm)