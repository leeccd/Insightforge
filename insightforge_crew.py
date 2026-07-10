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

qwen_llm = LLM(
    model="openrouter/qwen/qwen-2.5-72b-instruct",
    #api_key=os.getenv("OPENAI_API_KEY"), LOCAL DEPLOYMENT
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# 🪄 THE MAGIC: Read our business strategy from the external JSON file
with open('content_calendar.json', 'r') as f:
    calendar = json.load(f)

# For this run, let's use Week 1. (Next week, you just change this to calendar[1])
current_week_data = calendar[0] 
topic = current_week_data["topic"]
audience = current_week_data["target_audience"]

print(f"🔥 InsightForge is now forging insights on: '{topic}'")
print(f"🎯 Target Audience: '{audience}'\n")

# ==========================================
# 2. THE CUSTOM SEARCH TOOL (With Safety Net)
# ==========================================
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
        # 🛡️ IMPROVEMENT #3: If the search fails, we don't crash. We tell the AI to adjust.
        return f"Search failed due to rate limiting. Error: {str(e)}. Please try a simpler, broader search query."

# ==========================================
# 3. THE CREW (Dynamic & Context-Aware)
# ==========================================

# EMPLOYEE 1: THE RESEARCHER
researcher = Agent(
    role="Senior Market Researcher",
    goal="Find raw, unfiltered facts and data from the web.",
    backstory="You are a gritty researcher who digs deep into the web. You do not summarize; you just gather the raw facts.",
    verbose=True,
    tools=[search_internet],
    llm=qwen_llm
)

# Notice the {topic} and {audience} variables injected via f-strings!
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
    verbose=True,
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
    verbose=True,
    llm=qwen_llm
)

editing_task = Task(
    description=f"Take the analyst's summary and format it into a clean, professional newsletter. Include a catchy title, an intro, and a 'Key Takeaways' bulleted list at the bottom. Ensure the tone is highly engaging for: {audience}.",
    expected_output="A beautifully formatted markdown newsletter.",
    agent=editor,
    context=[analysis_task] 
)

# ==========================================
# 4. EXECUTION
# ==========================================
crew = Crew(
    agents=[researcher, analyst, editor],
    tasks=[research_task, analysis_task, editing_task],
    process=Process.sequential,
    verbose=True
)

print("Sending the full InsightForge team to work... grab a coffee, this takes a minute or two!\n")
result = crew.kickoff()

print("\n\n🎉🎉🎉 FINAL INSIGHTFORGE NEWSLETTER 🎉🎉🎉")
print(result)