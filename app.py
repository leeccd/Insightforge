import streamlit as st
import os

# ==========================================
# FORCE SET THE API KEY HERE
# ==========================================
# Paste your actual OpenRouter key between the quotes below:
#os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-"
# ==========================================

from dotenv import load_dotenv
# ... (leave the rest of the code exactly as it is)

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from duckduckgo_search import DDGS

# ==========================================
# 1. SETUP & INITIALIZATION
# ==========================================
# Set page config for a nice browser tab title and icon
st.set_page_config(page_title="InsightForge", page_icon="🚀", layout="wide")

# Load environment variables
load_dotenv()

# Cache the LLM so it doesn't reload every time you click a button
@st.cache_resource
def get_qwen_llm():
    return LLM(
        model="openrouter/qwen/qwen-2.5-72b-instruct",
        api_key=os.getenv("OPENROUTER_API_KEY") # Make sure this is in your .env!
    )

# ==========================================
# 2. CUSTOM TOOL
# ==========================================
@tool("DuckDuckGo Search")
def search_internet(query: str) -> str:
    """Useful for when you need to search the internet for current information."""
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=5)]
        if not results:
            return "No results found."
        output = ""
        for r in results:
            output += f"Title: {r['title']}\nSnippet: {r['body']}\nURL: {r['href']}\n\n"
        return output

# ==========================================
# 3. THE CREWAI BACKEND LOGIC
# ==========================================
def run_insightforge(topic: str, audience: str, llm):
    """Runs the 3-agent crew and returns the final newsletter string."""
    
    # EMPLOYEE 1: THE RESEARCHER
    researcher = Agent(
        role="Senior Market Researcher",
        goal="Find raw, unfiltered facts and data from the web.",
        backstory="You are a gritty researcher who digs deep into the web. You do not summarize; you just gather the raw facts.",
        verbose=False, # Set to False to keep Streamlit logs clean
        tools=[search_internet],
        llm=llm
    )
    
    research_task = Task(
        description=f"Research the latest advancements in: {topic}. Focus specifically on facts relevant to: {audience}. Find 3 major breakthroughs.",
        expected_output="A raw, bulleted list of 3 major breakthroughs with their sources.",
        agent=researcher
    )

    # EMPLOYEE 2: THE ANALYST
    analyst = Agent(
        role="Data Analyst",
        goal="Find the most important trends in the raw data.",
        backstory="You are an expert at reading raw data and pulling out the 'so what?'. You write clear, professional executive summaries.",
        verbose=False,
        llm=llm
    )

    analysis_task = Task(
        description="Review the researcher's raw notes. Write a 2-paragraph executive summary explaining why these 3 breakthroughs matter to the world.",
        expected_output="A professional 2-paragraph executive summary.",
        agent=analyst,
        context=[research_task]
    )

    # EMPLOYEE 3: THE EDITOR
    editor = Agent(
        role="Chief Editor",
        goal="Format the summary into a beautiful, easy-to-read newsletter format.",
        backstory="You have a keen eye for formatting. You take dry summaries and turn them into engaging newsletters with catchy titles.",
        verbose=False,
        llm=llm
    )

    editing_task = Task(
        description="Take the analyst's summary and format it into a clean, professional newsletter. Include a catchy title, an intro, and a 'Key Takeaways' bulleted list at the bottom.",
        expected_output="A beautifully formatted markdown newsletter.",
        agent=editor,
        context=[analysis_task]
    )

    # FORM THE CREW
    crew = Crew(
        agents=[researcher, analyst, editor],
        tasks=[research_task, analysis_task, editing_task],
        process=Process.sequential,
        verbose=False
    )

    # Kickoff and return raw text
    result = crew.kickoff()
    return result.raw

# ==========================================
# 4. THE STREAMLIT FRONTEND (UI)
# ==========================================
st.title("🚀 InsightForge AI Newsletter Generator")
st.markdown("Generate professional, researched newsletters in seconds using a multi-agent AI crew.")

# Input fields
col1, col2 = st.columns(2)
with col1:
    topic = st.text_input("📌 Enter your Topic:", placeholder="e.g., Quantum Computing in Healthcare")
with col2:
    audience = st.text_input("👥 Enter your Target Audience:", placeholder="e.g., Hospital Administrators")

# Generate Button
if st.button("✨ Generate Newsletter", type="primary", use_container_width=True):
    if not topic or not audience:
        st.warning("Please fill in both the Topic and the Target Audience!")
    else:
        # Initialize session state to hold the result
        if "generated_newsletter" not in st.session_state:
            st.session_state.generated_newsletter = None
            
        with st.spinner("🧠 AI Agents are researching, analyzing, and editing... This may take a minute."):
            try:
                # Get the cached LLM
                llm = get_qwen_llm()
                
                # Run the crew
                final_text = run_insightforge(topic, audience, llm)
                
                # Save to session state
                st.session_state.generated_newsletter = final_text
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.session_state.generated_newsletter = None

# Display the result if it exists in session state
if st.session_state.get("generated_newsletter"):
    st.markdown("---")
    st.subheader("📰 Your Generated Newsletter:")
    # Render the markdown beautifully
    st.markdown(st.session_state.generated_newsletter)
    
    # Add a download button
    st.download_button(
        label="📥 Download as Markdown",
        data=st.session_state.generated_newsletter,
        file_name="insightforge_newsletter.md",
        mime="text/markdown"
    )