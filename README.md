# EUC Assessment Agent Team

A multi-agent system for automated End User Computing (EUC) assessments using LangGraph and Pydantic.

## Overview

This project implements a team of specialized AI agents that work together to assess End User Computing (EUC) technologies, features, or proposed changes. The agents collaborate to gather context, perform research, design solutions, and analyze implications across multiple domains (security, cost, licensing, support, user impact), delivering a comprehensive assessment report.

## Project Structure

```
euc_assessment/
├── app.py                  # Main Streamlit application
├── main.py                 # Entry point for the agent system
├── config/                 # Configuration files
├── data/                   # Data storage
│   └── assessments/        # Saved assessment results
├── src/                    # Source code
│   ├── agents/             # Agent implementations
│   │   ├── __init__.py
│   │   ├── orchestrator.py # Lead Orchestrator agent
│   │   ├── context.py      # Context & Requirements agent
│   │   ├── research.py     # Research & Feasibility agent
│   │   └── ...             # Other specialist agents
│   ├── models/             # Pydantic models
│   │   ├── __init__.py
│   │   └── state.py        # State definitions
│   ├── tools/              # Tool implementations
│   │   ├── __init__.py
│   │   └── web_search.py   # Web search tool
│   └── utils/              # Utility functions
│       ├── __init__.py
│       └── helpers.py      # Helper functions
└── tests/                  # Test files
    ├── __init__.py
    └── test_agents.py      # Agent tests
```

## Installation

1. Clone the repository
2. Set up a Python virtual environment (Python 3.8+):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements_euc.txt
   ```
4. Configure environment variables by copying `.env.example` to `.env` and adding your API keys:
   ```
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Usage

### Running the Streamlit App

To use the web interface:

```
streamlit run app.py
```

This will open a browser window with the EUC Assessment tool.

### Running from Command Line

To run an assessment directly from the command line:

```
python main.py
```

This uses the example assessment request in `main.py`. Modify the `example_request` variable to change the assessment input.

## Development Status

### Completed
- ✅ Environment & Configuration Setup (P1.1)
- ✅ Initial State Model Definition (P1.2)
- ✅ LangGraph Graph Initialization (P1.3)
- ✅ Lead Orchestrator Agent Implementation (P1.4)
- ✅ Context & Requirements Agent Implementation (P1.5)
- ✅ Research & Feasibility Agent Implementation (P1.6)
- ✅ Initial Workflow Edge Definition (P1.7)
- ✅ Solution Architect Agent Implementation (P2.1)
- ✅ Security Analyst Agent Implementation (P2.2)
- ✅ Licensing Specialist Agent Implementation (P2.3)
- ✅ Implementation Engineer Agent Implementation (P2.4)

### In Progress
- 🔄 Basic End-to-End Test (P1.8)
- 🔄 State Model Refinement (P1.9)
- 🔄 Support & Operations Agent (P2.5)

### Upcoming
- User Experience & Enablement Agent (P2.6)
- Cost & Value Analyst Agent (P2.7)

## Development Guidelines

- Follow PEP 8 coding standards
- Use type hints for all functions and classes
- Write docstrings in Google style
- Maintain test coverage (minimum 80%)
- Use black for code formatting

## License

This project is licensed under the MIT License.

## Acknowledgements

Based on the Archon framework by [coleam00](https://github.com/coleam00/archon).
