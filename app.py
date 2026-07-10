import streamlit as st
from insightforge_crew import run_insightforge

st.set_page_config(page_title="InsightForge", page_icon="🔥", layout="wide")

st.title("🔥 InsightForge")
st.markdown("### Turn any topic into actionable intelligence.")
st.markdown("---")

# Get inputs from the user
topic = st.text_input("What topic should we forge insights on?", placeholder="e.g., AI in Senior Wellness...")
audience = st.text_input("Who is the target audience?", placeholder="e.g., 55+ wellness seekers...", value="The general public")

if st.button("🚀 Forge Insights", type="primary", use_container_width=True):
    if not topic:
        st.warning("Please enter a topic first!")
    else:
        with st.status(f"🔥 Forging insights on: **{topic}**...", expanded=True) as status:
            st.write("🔍 **Researcher** is scanning the web...")
            st.write("📊 **Analyst** is identifying key trends...")
            st.write("📰 **Editor** is formatting the newsletter...")
            
            try:
                # 🪄 Call the function with BOTH variables
                final_newsletter = run_insightforge(topic, audience)
                status.update(label="✅ Insight Forging Complete!", state="complete", expanded=False)
            except Exception as e:
                st.error(f"⚠️ An error occurred: {e}")
                st.stop()

        st.markdown("---")
        st.subheader("📰 Your Forged Insight Newsletter")
        st.markdown(final_newsletter)
        
        st.download_button(
            label="📥 Download as Markdown",
            data=final_newsletter,
            file_name=f"insightforge_{topic.replace(' ', '_')}.md",
            mime="text/markdown"
        )