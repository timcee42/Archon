"""
Streamlit application for the EUC Assessment Agent Team.

This script implements a web interface for running EUC assessments using Streamlit.
"""

import logging
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from main import run_assessment
from src.utils.helpers import format_report, save_json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="EUC Assessment Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_session_state():
    """Initialize session state variables."""
    if "assessment_results" not in st.session_state:
        st.session_state.assessment_results = None
    if "is_assessing" not in st.session_state:
        st.session_state.is_assessing = False
    if "current_phase" not in st.session_state:
        st.session_state.current_phase = None
    if "assessment_history" not in st.session_state:
        st.session_state.assessment_history = []


def run_eutc_assessment(request):
    """
    Run an assessment and update the session state.
    
    Args:
        request: The assessment request
    """
    try:
        st.session_state.is_assessing = True
        st.session_state.current_phase = "Starting assessment..."

        # Run the assessment
        result = run_assessment(request)
        
        # Process and store the results
        st.session_state.assessment_results = result
        
        # Save the assessment to history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.assessment_history.append({
            "timestamp": timestamp,
            "request": request,
            "result": result,
        })
        
        # Save results to file
        os.makedirs("data/assessments", exist_ok=True)
        filename = f"data/assessments/assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_json(result.dict(), filename)
        
    except Exception as e:
        logger.error(f"Error running assessment: {e}")
        st.error(f"An error occurred while running the assessment: {e}")
    finally:
        st.session_state.is_assessing = False
        st.session_state.current_phase = None


def main():
    """Main application logic."""
    initialize_session_state()
    
    # Sidebar
    st.sidebar.title("EUC Assessment Agent")
    st.sidebar.image("https://via.placeholder.com/150?text=EUC+Agent", width=150)
    
    # Application tabs
    tab1, tab2, tab3 = st.tabs(["New Assessment", "Results", "History"])
    
    # Tab 1: New Assessment
    with tab1:
        st.header("End User Computing Assessment")
        st.write("""
        This tool helps assess End User Computing (EUC) technologies, features, or proposed changes
        using a team of specialized AI agents. The agents will analyze your request from multiple perspectives
        including architecture, security, licensing, implementation, support, and user experience.
        """)
        
        # Assessment input form
        with st.form("assessment_form"):
            assessment_request = st.text_area(
                "Describe what you would like to assess:",
                height=150,
                help="Provide details about the EUC technology, feature, or change you want to assess."
            )
            
            # Optional organization context
            st.subheader("Optional Organization Context", help="This information helps provide a more accurate assessment")
            col1, col2 = st.columns(2)
            with col1:
                company_size = st.text_input("Company Size (e.g., number of employees)")
                industry = st.text_input("Industry")
            with col2:
                tech_stack = st.text_input("Current Technology Stack (comma separated)")
                compliance = st.text_input("Compliance Requirements (comma separated)")
            
            submit_button = st.form_submit_button("Run Assessment")
            
            if submit_button and assessment_request:
                # Enhance the request with organization context if provided
                enhanced_request = assessment_request
                context_parts = []
                if company_size:
                    context_parts.append(f"Company Size: {company_size}")
                if industry:
                    context_parts.append(f"Industry: {industry}")
                if tech_stack:
                    context_parts.append(f"Current Technology Stack: {tech_stack}")
                if compliance:
                    context_parts.append(f"Compliance Requirements: {compliance}")
                
                if context_parts:
                    enhanced_request += "\n\nAdditional Organization Context:\n" + "\n".join(context_parts)
                
                # Run the assessment
                run_eutc_assessment(enhanced_request)
                
                # Switch to results tab
                tab2.set_active(tab2)
        
        # Assessment in progress indicator
        if st.session_state.is_assessing:
            st.info(f"Assessment in progress... Current phase: {st.session_state.current_phase}")
            st.spinner("Running agents...")
    
    # Tab 2: Results
    with tab2:
        st.header("Assessment Results")
        
        if st.session_state.assessment_results:
            results = st.session_state.assessment_results
            
            # Display the assessment report
            if results.final_report:
                st.markdown(results.final_report)
            else:
                # Generate a report from the current state
                report = format_report(results.dict())
                st.markdown(report)
                
                # Show progress
                st.subheader("Assessment Progress")
                phases = [
                    "context_requirements", "research", "architecture", 
                    "security", "licensing", "implementation", "support", 
                    "user_experience", "cost", "report"
                ]
                completed = results.completed_phases
                
                progress = len(completed) / len(phases)
                st.progress(progress)
                st.write(f"Completed phases: {', '.join(completed)}")
                st.write(f"Current phase: {results.current_phase}")
        else:
            st.info("No assessment results yet. Run an assessment from the 'New Assessment' tab.")
    
    # Tab 3: History
    with tab3:
        st.header("Assessment History")
        
        if st.session_state.assessment_history:
            for i, assessment in enumerate(reversed(st.session_state.assessment_history)):
                with st.expander(f"Assessment {i+1} - {assessment['timestamp']}"):
                    st.write(f"**Request:**\n{assessment['request']}")
                    
                    if "result" in assessment:
                        result = assessment["result"]
                        if hasattr(result, "final_report") and result.final_report:
                            st.markdown(result.final_report)
                        else:
                            # Generate a report from the state
                            report = format_report(result.dict())
                            st.markdown(report)
        else:
            st.info("No assessment history yet.")


if __name__ == "__main__":
    main() 