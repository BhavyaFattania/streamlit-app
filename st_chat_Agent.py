import streamlit as st
import openai
from langchain.callbacks import StreamlitCallbackHandler
from langchain.tools import DuckDuckGoSearchRun
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentType, initialize_agent, load_tools,Tool
from langchain.callbacks import StreamlitCallbackHandler
from langchain import LLMMathChain
from langchain.memory import ConversationBufferMemory
from langchain.memory import StreamlitChatMessageHistory

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    st.write("***Agent is OPENAI_FUNCTIONS.***\n\n***Tools are llm_math and duckduckgo-search.***\
             \n\n***Conversation history can be kept.***\n\n***To learn more, please visit the following links!***")
    "[OpenAI functions](https://python.langchain.com/docs/modules/agents/agent_types/openai_functions_agent)"
    "[DuckDuckGo Search](https://python.langchain.com/docs/integrations/tools/ddg)"
    "[View the source code](https://github.com/tsuzukia21/streamlit-app/blob/main/st_chat_Agent.py)"
    openai.api_key = openai_api_key

st.title("Agent by Streamlit") # タイトルの設定

st_callback = StreamlitCallbackHandler(st.container())
search = DuckDuckGoSearchRun()
llm = ChatOpenAI(temperature=0, streaming=True, model="gpt-3.5-turbo")
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=False)

template = """You are an AI chatbot having a conversation with a human.
{history}
Human: {human_input}
AI: """

attrs=["messages_agent","agent_kwargs"]
for attr in attrs:
    if attr not in st.session_state:
        st.session_state[attr] = []
if "Clear" not in st.session_state:
    st.session_state.Clear = False

msgs = StreamlitChatMessageHistory(key="special_app_key")
memory = ConversationBufferMemory(memory_key="history", chat_memory=msgs)
tools = [
    Tool(
        name = "ddg-search",
        func=search.run,
        description="useful for when you need to answer questions about current events.. You should ask targeted questions"
    ),
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="useful for when you need to answer questions about math"
    ),
]
agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=False,memory=memory)

# Display chat messages_agent from history on app rerun
for message in st.session_state.messages_agent:
    if not message["role"]=="system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"],unsafe_allow_html=True)

if user_prompt := st.chat_input("Send a message"):
    if not openai_api_key:
        st.error('Please add your OpenAI API key to continue.', icon="🚨")
        st.stop()
    st.session_state.messages_agent.append({"role": "user", "content": user_prompt})
    st.chat_message("user").write(user_prompt)
    prompt = template.format(history=msgs.messages, human_input=user_prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(prompt, callbacks=[st_callback])
        st.write(response)
    st.session_state.messages_agent.append({"role": "assistant", "content": response})
    st.session_state.Clear = True # チャット履歴のクリアボタンを有効にする

# チャット履歴をクリアするボタンが押されたら、メッセージをリセット
if st.session_state.Clear:
    if st.button('clear chat history'):
        st.session_state.messages_agent = [] # メッセージのリセット
        response = ""
        msgs.clear()
        memory.clear()
        st.session_state.Clear = False # クリア状態をリセット
        st.experimental_rerun() # 画面を更新