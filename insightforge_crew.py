import os
import json
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from duckduckgo_search import DDGS

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
load_dotenv()

# 🪄 THE CUSTOM SEARCH TOOL (With Safety Net)
@tool("DuckDuckGo Search")
def search_internet(query: str) -> str:
    """Useful for when you need to search the internet for current information."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
            if not results:
                return "No results found."
            output = ""
            for r in results:
                output += f"Title: {r['title']}\nSnippet: {r['body']}\nURL: {r['href']}\n\n"
            return output
    except Exception as e:
        return f"Search failed due to rate limiting. Error: {str(e)}. Please try a simpler, broader search query."

# ==========================================
# 🛡️ 2. THE STREAMLIT-SAFE FUNCTION
# ==========================================
def run_insightforge(topic: str, audience: str) -> str:
    """
    This function builds and runs the Crew. 
    Streamlit will call this ONLY when the user clicks the button.
    """
    
    # 1. Connect to our reliable 72B Qwen brain via OpenRouter
    qwen_llm = LLM(
        model="openrouter/qwen/qwen-2.5-72b-instruct",
        api_key=os.getenv("OPENROUTER_API_KEY") # 🪄 Must match Streamlit Secrets exactly
    )

    # EMPLOYEE 1: THE RESEARCHER
    researcher = Agent(
        role="Senior Market Researcher",
        goal="Find raw, unfiltered facts and data from the web.",
        backstory="You are a gritty researcher who digs deep into the web. You do not summarize; you just gather the raw facts.",
        verbose=False, # Set to False to keep Streamlit logs clean
        tools=[search_internet],
        llm=qwen_llm
    )

    research_task = Task(
        description=f"Research the latest advancements in: {topic}. Focus specifically on facts and data relevant to: {audience}. Find 3 major breakthroughs or tools.",
        expected_output="A raw, bulleted list of 3 major breakthroughs with their sources.",
        agent=researcher
    )

    # EMPLOYEE 2: THE ANALYST
    analyst = Agent(
        role="Data Analyst",
        goal="Find the most important trends in the raw data for the specific target audience.",
        backstory="You are an expert at reading raw data and pulling out the 'so what?'. You write clear, professional executive summaries tailored to the reader.",
        verbose=False,
        llm=qwen_llm 
    )

    analysis_task = Task(
        description=f"Review the researcher's raw notes. Write a 2-paragraph executive summary explaining why these 3 breakthroughs matter specifically to: {audience}.",
        expected_output="A professional 2-paragraph executive summary.",
        agent=analyst,
        context=[research_task] 
    )

    # EMPLOYEE 3: THE EDITOR
    editor = Agent(
        role="Chief Editor",
        goal="Format the summary into a beautiful, easy-to-read newsletter format.",
        backstory="You have a keen eye for formatting. You take dry summaries and turn them into engaging, easy-to-read newsletters with catchy titles.",
        verbose=False,
        llm=qwen_llm
    )

    editing_task = Task(
        description=f"Take the analyst's summary and format it into a clean, professional newsletter. Include a catchy title, an intro, and a 'Key Takeaways' bulleted list at the bottom. Ensure the tone is highly engaging for: {audience}.",
        expected_output="A beautifully formatted markdown newsletter.",
        agent=editor,
        context=[analysis_task] 
    )

    # FORM THE CREW AND START WORKING!
    crew = Crew(
        agents=[researcher, analyst, editor],
        tasks=[research_task, analysis_task, editing_task],
        process=Process.sequential,
        verbose=False
    )

    # Kickoff the crew and return the final result to Streamlit
    result = crew.kickoff()
    return str(result)

# ==========================================
# 🛡️ 3. LOCAL TESTING GUARD
# ==========================================
# This ensures the code ONLY runs automatically if you execute this file directly 
# from your terminal. It prevents Streamlit from crashing on import.
if __name__ == "__main__":
    print("🔥 Running InsightForge locally for testing...")
    
    # Load the JSON calendar for local testing
    try:
        with open('content_calendar.json', 'r') as f:
            calendar = json.load(f)
        current_week_data = calendar[0] 
        test_topic = current_week_data["topic"]
        test_audience = current_week_data["target_audience"]
    except FileNotFoundError:
        test_topic = "Renewable Energy"
        test_audience = "The general public"

    final_newsletter = run_insightforge(test_topic, test_audience)
    print("\n\n🎉🎉🎉 FINAL INSIGHTFORGE NEWSLETTER 🎉🎉🎉")
    print(final_newsletter)