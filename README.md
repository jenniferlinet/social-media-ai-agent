# 🚀 Social Media AI Agent

A smart little tool that writes social media posts for you, generates an image to go with them, and posts everything straight to Discord — all with one click.

Built with Azure OpenAI, LangGraph, and Streamlit.

---

## What does it do?

You give it a topic (like *"AI in healthcare"*), and it:

1. **Writes a short, catchy social media post** using GPT
2. **Creates a simple image** with the post text on it
3. **Lets you preview everything** before posting
4. **Posts it to Discord** automatically via a webhook — if you approve it

---

## How it works (the simple version)

Think of it like a mini assembly line:

```
Your idea → AI writes the post → Image gets created → You approve → Posted to Discord
```

Each step is handled by a separate "node" in the agent, and they pass information between each other automatically.

---

## Tech stack

| Tool | What it does |
|------|-------------|
| **Azure OpenAI (GPT)** | Writes the social media post |
| **LangChain** | Connects and manages the AI model |
| **LangGraph** | Controls the step-by-step agent flow |
| **Pillow (PIL)** | Creates the text image |
| **Discord Webhook** | Posts the content to your Discord channel |
| **Streamlit** | The web UI you interact with |

---

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/jenniferlinet/social-media-ai-agent.git
cd social-media-ai-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# or
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your `.env` file

Create a file called `.env` in the project folder and add:

```
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_id/your_token
```

> ⚠️ Never share or upload this file. It's already in `.gitignore` to keep it safe.

### 5. Run the app

```bash
streamlit run ui.py
```

Then open your browser at: **http://localhost:8501**

---

## How to use it

1. Type in your topic or idea
2. Click **✨ Generate Content**
3. Preview the post and image
4. Hit **Approve** to post it to Discord, or **Discard** to start over

---

## Project structure

```
social-media-ai-agent/
├── ui.py               # The main Streamlit app
├── requirements.txt    # All the dependencies
├── .env                # Your secret keys (not uploaded to GitHub)
├── .env.example        # A safe template showing what keys are needed
└── .gitignore          # Keeps sensitive files out of GitHub
```

---

## Requirements

```
streamlit
requests
python-dotenv
pillow
langchain
langchain-core
langchain-openai
langgraph
```

---

## Notes

- The app pauses after generating the post so you can review it before anything gets posted — you're always in control.
- The image is created locally using Pillow (no external image API needed).
- Make sure your Discord webhook is set up and active before running.

---

Made with 💙 using Azure OpenAI + LangGraph + Streamlit
