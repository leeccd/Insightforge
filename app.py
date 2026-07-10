import streamlit as st
from insightforge_crew import run_insightforge

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="InsightForge | Enterprise AI Intelligence", 
    page_icon="💎", 
    layout="wide"
)

# ==========================================
# 2. CUSTOM CSS FOR PREMIUM FEEL
# ==========================================
st.markdown("""
    <style>
    /* Make the main header look like a premium gradient */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00A3FF, #00E5FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        letter-spacing: -1px;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #888;
        margin-top: 5px;
        margin-bottom: 20px;
    }
    /* Make the primary button look like a high-end SaaS button */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        font-weight: 600;
        font-size: 1.1rem;
        background: linear-gradient(90deg, #00A3FF, #0072FF);
        color: white;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 163, 255, 0.4);
    }
    /* Hide the default Streamlit footer/menu to make it look like a standalone app */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. THE SIDEBAR (Configuration Panel)
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")
    
    # Inputs moved to the sidebar for a cleaner main screen
    topic = st.text_input("🎯 Research Topic", placeholder="e.g., AI in Senior Wellness")
    audience = st.text_input("👥 Target Audience", value="Business Professionals")
    
    st.markdown("---")
    st.caption("💡 **Pro Tip:** Be highly specific with your target audience to get the most valuable, actionable insights.")
    
    # Add a fake "Premium" badge to build perceived value
    st.success("🚀 **Pro Tier Active**")

# ==========================================
# 4. THE MAIN DASHBOARD (Hero & Output)
# ==========================================

# Beautiful Gradient Header
st.markdown('<p class="main-header">InsightForge</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Enterprise-grade AI research for actionable business intelligence.</p>', unsafe_allow_html=True)

# If we haven't generated an insight yet, show a welcome message
if "last_insight" not in st.session_state:
    st.markdown("### Welcome to your AI Intelligence Dashboard.")
    st.markdown("Configure your research parameters in the **sidebar** and click **Forge Insights** to generate a comprehensive, multi-agent research report in seconds.")
    
    # Add some nice placeholder columns to make the empty state look professional
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Agents Deployed", value="3")
    with col2:
        st.metric(label="Data Sources", value="Live Web")
    with col3:
        st.metric(label="Processing Time", value="~60s")

# The "Forge" Button
if st.button("🚀 FORGE INSIGHTS", type="primary"):
    if not topic:
        st.sidebar.warning("⚠️ Please enter a Research Topic in the sidebar!")
    else:
        # Create a beautiful status container
        with st.status(f"🔥 Deploying InsightForge Agents for: **{topic}**...", expanded=True) as status:
            st.write("🔍 **Researcher Agent** is scanning the live web for raw data...")
            st.write("📊 **Analyst Agent** is identifying key trends and synthesizing data...")
            st.write("📰 **Editor Agent** is formatting the final executive newsletter...")
            
            try:
                # Call the engine
                final_newsletter = run_insightforge(topic, audience)
                
                # Save to session state so it stays on screen
                st.session_state.last_insight = final_newsletter
                st.session_state.last_topic = topic
                
                status.update(label="✅ Intelligence Gathering Complete!", state="complete", expanded=False)
            except Exception as e:
                st.error(f"⚠️ An error occurred during processing: {e}")
                st.stop()

# Display the result if we have one
if "last_insight" in st.session_state:
    st.markdown("---")
    
    # Create a nice header for the result
    st.markdown(f"### 📰 Executive Briefing: {st.session_state.last_topic}")
    
    # Display the markdown beautifully
    st.markdown(st.session_state.last_insight)
    
    st.markdown("---")
    
    # Professional download options
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Download as Markdown (.md)",
            data=st.session_state.last_insight,
            file_name=f"InsightForge_{st.session_state.last_topic.replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col2:
        st.download_button(
            label="📄 Download as Text (.txt)",
            data=st.session_state.last_insight,
            file_name=f"InsightForge_{st.session_state.last_topic.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )