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
2. Set up a Python virtual environment (Python 3.8+)
3. Install dependencies:
   ```
   pip install -r requirements_euc.txt
   ```
4. Configure environment variables (see Configuration section)

## Configuration

Create a `.env` file in the project root with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Usage

Run the Streamlit application:

```
streamlit run app.py
```

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