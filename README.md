# AI Executive Suite

An AI-powered executive decision-making simulation using **Groq** to train and evaluate AI agents in CEO, CFO, and CTO roles.

## Overview

This project simulates executive decision-making in a startup environment using reinforcement learning principles. AI agents powered by **Groq (llama-3.3-70b-versatile)** make strategic decisions across three executive roles, learning from past failures to improve performance.

## Features

- **AI-Powered Decisions**: Uses Groq LLM for intelligent executive decision-making
- **Failure Learning**: Agents learn from past mistakes stored in memory
- **Multi-Role Simulation**: CEO, CFO, and CTO roles with realistic business scenarios
- **Real-time Chat**: Interactive AI executive assistant
- **Performance Tracking**: Comprehensive scoring and analytics
- **Streamlit UI**: Modern web interface for easy interaction

## Roles & Difficulty

### CEO (Chief Executive Officer) [Difficulty: Easy]
- **Focus**: Revenue growth and market expansion
- **Actions**: `expand_market`, `reduce_costs`, `launch_feature`, `do_nothing`
- **Metrics**: Revenue targets ($3,000), user growth (300 users)

### CFO (Chief Financial Officer) [Difficulty: Medium]
- **Focus**: Financial health and profitability
- **Actions**: `cut_costs`, `increase_marketing`, `invest_growth`, `hold`
- **Metrics**: Cash runway (12+ months), profit margins

### CTO (Chief Technology Officer) [Difficulty: Hard]
- **Focus**: Technical excellence and system reliability
- **Actions**: `fix_bugs`, `build_feature`, `scale_infrastructure`, `ignore`
- **Metrics**: Bug reduction, system load management, user satisfaction

## Environment API Specification

- **Action Space**: The agent emits exactly one categorical string identifying its action (e.g. `"increase_marketing"`). No JSON parsing is required for simple inference.
- **Observation Space**: A JSON-compatible dictionary (state) containing integer and float properties defining the company's vital signs: `revenue`, `expenses`, `cash`, `users`, `burn_rate`, `bug_count`, `system_load`. 
- **Reward Function**: Dense rewards ranging incrementally. Every positive shift in step-over-step metrics (e.g. rising revenues, dropping bugs) contributes 0.1 to 1.0 immediate rewards, making it an ideal continuous learning signal.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Get Groq API Key (Free)**:
   - Sign up at [Groq Console](https://console.groq.com/)
   - Generate a free API key

3. **Set API Key**:
   ```bash
   # Windows (PowerShell)
   $env:GROQ_API_KEY="your_key_here"

   # Or add to a .env file
   GROQ_API_KEY=your_key_here
   ```

4. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

5. **Or run with Docker**:
   ```bash
   docker build -t ai-executive-suite .
   docker run -p 8501:8501 -e GROQ_API_KEY=your_key_here ai-executive-suite
   ```

## Usage

1. Set your `GROQ_API_KEY` environment variable
2. Navigate between different sections:
   - **Simulation**: Run AI-powered executive simulations
   - **Chat**: Interact with AI executives for advice
   - **Analytics**: View performance metrics and learning progress

## Architecture

- **openenv/**: Core simulation environment package
  - `tasks/`: Individual role implementations (CEO/CFO/CTO)
  - `graders/`: Performance evaluation functions
  - `models/`: Pydantic data models
- **ai_decisions.py**: Groq-powered decision making with fallback logic
- **failure_memory.py**: Learning system for past failures
- **simulation.py**: Multi-step simulation coordinator
- **chat.py**: AI chat interface using Groq

## Learning System

The AI agents learn from failures through:
- **Failure Memory**: JSON-based storage of poor decisions and their contexts
- **Adaptive Decision Making**: Groq considers recent failures when making new decisions
- **Performance Feedback**: Real-time scoring helps agents understand decision quality

## Contributing

This project demonstrates AI executive decision-making and can be extended with:
- Additional executive roles
- More complex business scenarios
- Advanced learning algorithms
- Integration with other AI models

## Scoring

Each environment has a grader that evaluates the final state on a scale of 0.0 to 1.0:

- **CEO**: Normalized score based on revenue and user growth compared to initial values.
- **CFO**: Score combining profit margin and financial runway (cash/burn rate).
- **CTO**: Score based on bug reduction, system load management, and user satisfaction.

Higher scores indicate better performance in the respective role.