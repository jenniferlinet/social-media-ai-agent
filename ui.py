import streamlit as st
import os
import uuid
from typing import TypedDict
import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# LangGraph / LangChain imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Use Azure OpenAI (modern replacement for Ollama)
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage


# ===============================
# 1️⃣ SETUP & AGENT STATE
# ===============================

load_dotenv()

# Try to initialize Azure OpenAI LLM
try:
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version="2025-01-01-preview",
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )
except Exception as e:
    llm = None
    st.error(f"⚠️ Failed to initialize Azure OpenAI: {e}")

class AgentState(TypedDict):
    prompt: str
    post: str
    image_path: str


# ===============================
# 2️⃣ CACHED GRAPH & MEMORY SETUP
# ===============================

@st.cache_resource
def setup_agent():
    """Create and compile the LangGraph agent and its memory."""
    memory = MemorySaver()
    graph = StateGraph(AgentState)

    # --- Node 1: Create social media post ---
    def create_post_node(state: AgentState):
        if not llm:
            st.error("Azure OpenAI not configured properly. Check your .env keys.")
            return state

        prompt = f"Create a short, catchy, and engaging social media post about: {state['prompt']}"
        response = llm.invoke([HumanMessage(content=prompt)])
        state["post"] = response.content
        return state

    # --- Node 2: Generate an image with the text ---
    def generate_image_node(state: AgentState):
        image = Image.new('RGB', (800, 400), color='white')
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except IOError:
            font = ImageFont.load_default()

        # Word wrap text
        lines = []
        words = state['post'].split()
        current_line = ""
        for word in words:
            if len(current_line + " " + word) < 50:
                current_line += " " + word
            else:
                lines.append(current_line.strip())
                current_line = word
        lines.append(current_line.strip())

        # Draw text
        y_text = 150
        for line in lines:
            draw.text((40, y_text), line, font=font, fill='black')
            y_text += 40

        image_path = f"temp_post_image_{uuid.uuid4()}.png"
        image.save(image_path)
        state["image_path"] = image_path
        return state

    # --- Node 3: Post to Discord ---
    def post_to_discord_node(state: AgentState):
        """Posts the content to a Discord channel using a Webhook."""
        st.write("🌀 Posting to Discord...")

        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        if not webhook_url:
            st.error("Discord Webhook URL not found in .env file.")
            return state

        try:
            with open(state["image_path"], "rb") as f:
                data = {"content": state["post"]}
                files = {"file": (os.path.basename(state["image_path"]), f)}
                response = requests.post(webhook_url, data=data, files=files)
                response.raise_for_status()

            st.success("✅ Successfully posted to Discord!")
        except Exception as e:
            st.error(f"Failed to post to Discord: {e}")
        finally:
            if os.path.exists(state["image_path"]):
                os.remove(state["image_path"])
        return state

    # --- Graph structure ---
    graph.add_node("create_post", create_post_node)
    graph.add_node("generate_image", generate_image_node)
    graph.add_node("post_to_discord", post_to_discord_node)

    graph.set_entry_point("create_post")
    graph.add_edge("create_post", "generate_image")
    graph.add_edge("generate_image", "post_to_discord")
    graph.add_edge("post_to_discord", END)

    app = graph.compile(
        checkpointer=memory,
        interrupt_before=["post_to_discord"]
    )
    return app


app = setup_agent()


# ===============================
# 3️⃣ STREAMLIT UI
# ===============================

st.title("🚀 Social Media AI Agent (Azure OpenAI Edition)")
st.markdown("Generate creative posts + images, and auto-share them to Discord.")

if "agent_state" not in st.session_state:
    st.session_state.agent_state = None
if "thread" not in st.session_state:
    st.session_state.thread = None

user_input = st.text_input("💡 Enter your idea for a post (e.g., 'AI in healthcare')")

if st.button("✨ Generate Content"):
    if user_input:
        st.session_state.agent_state = None
        with st.spinner("🤖 Azure AI is crafting your post..."):
            thread = {"configurable": {"thread_id": str(uuid.uuid4())}}
            st.session_state.thread = thread

            try:
                result = app.invoke({"prompt": user_input}, thread)
                final_state = result
                st.session_state.agent_state = final_state
            except Exception as e:
                st.error(f"Generation failed: {e}")
    else:
        st.warning("Please enter an idea first.")

if st.session_state.agent_state:
    st.divider()
    st.subheader("📝 Generated Post Preview")

    post_content = st.session_state.agent_state.get("post")
    image_path = st.session_state.agent_state.get("image_path")

    st.write(post_content)
    if image_path and os.path.exists(image_path):
        st.image(image_path)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Approve & Post", type="primary"):
            with st.spinner("Posting to Discord..."):
                app.invoke(None, st.session_state.thread)
                st.session_state.agent_state = None
                st.session_state.thread = None
    with col2:
        if st.button("❌ Discard"):
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            st.session_state.agent_state = None
            st.session_state.thread = None
            st.info("Post discarded.")
