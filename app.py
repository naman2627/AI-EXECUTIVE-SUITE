# app.py
import re
import time
import streamlit as st

from simulation import SimulationRunner, run_quick_simulation
from chat import call_ai, build_conversation_prompt
from utils import display_chat_messages, render_step, safe_rerun
from db import create_user, get_user, save_chat, load_chats

st.set_page_config(page_title="AI Executive Suite", page_icon="??", layout="wide")

# -- Session state --------------------------------------------------------------
for key, default in [
    ("user", None),
    ("chat_history", []),
    ("simulation_results", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# -- CSS ------------------------------------------------------------------------
st.markdown("""
<style>
.main-header { font-size: 2.2rem; font-weight: 700; text-align: center; margin-bottom: 1.5rem; }
.role-card { background: #f0f2f6; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# LOGIN PAGE
# ------------------------------------------------------------------------------
def login_page():
    st.title("?? AI Executive Suite")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                user = get_user(username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.chat_history = [
                        {"role": r, "content": c} for r, c in load_chats(user[0])
                    ]
                    st.success("Login successful!")
                    time.sleep(0.8)
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    with tab2:
        with st.form("signup_form"):
            new_user = st.text_input("Username")
            new_pass = st.text_input("Password", type="password")
            if st.form_submit_button("Create Account"):
                try:
                    create_user(new_user, new_pass)
                    st.success("Account created! Please log in.")
                except Exception as e:
                    st.error(f"Could not create account: {e}")


# ------------------------------------------------------------------------------
# MAIN APP
# ------------------------------------------------------------------------------
def main_app():
    user_id = st.session_state.user[0]

    with st.sidebar:
        st.header("?? Controls")
        if st.button("?? Logout"):
            for k in ["user", "chat_history", "simulation_results"]:
                st.session_state[k] = None if k == "user" else ([] if k == "chat_history" else "")
            st.rerun()

        st.divider()
        if st.button("? Quick Simulation (5 steps)"):
            with st.spinner("Running quick simulation..."):
                scores = run_quick_simulation()
                st.session_state.simulation_results = {"final_scores": scores, "results": []}
            st.success(f"CEO: {scores['ceo']:.2f} | CFO: {scores['cfo']:.2f} | CTO: {scores['cto']:.2f}")

    st.markdown('<h1 class="main-header">?? AI Executive Suite</h1>', unsafe_allow_html=True)
    st.caption("AI-powered executive decision-making simulation powered by Groq")

    tab1, tab2, tab3, tab4 = st.tabs(["?? Simulation", "?? Strategy Advisor", "?? AI Chat", "?? Analytics"])

    with tab1:
        simulation_tab(user_id)
    with tab2:
        strategy_tab(user_id)
    with tab3:
        chat_tab(user_id)
    with tab4:
        analytics_tab()


# ------------------------------------------------------------------------------
# TAB 1: SIMULATION
# ------------------------------------------------------------------------------
def simulation_tab(user_id: int):
    st.header("?? Executive Simulation")

    col_params, col_run = st.columns([3, 1])

    with col_params:
        st.markdown("#### ?? CEO Parameters")
        c1, c2 = st.columns(2)
        with c1:
            revenue = st.number_input("Revenue ($)", value=2000, min_value=0)
        with c2:
            users = st.number_input("Users", value=100, min_value=0)

        st.markdown("#### ?? CFO Parameters")
        c1, c2, c3 = st.columns(3)
        with c1:
            cash = st.number_input("Cash ($)", value=5000, min_value=0)
        with c2:
            burn_rate = st.number_input("Burn Rate ($/mo)", value=500, min_value=0)
        with c3:
            expenses = st.number_input("Expenses ($)", value=2000, min_value=0)

    with col_run:
        st.markdown("#### Run")
        run_full = st.button("?? Full Run (10 steps)")
        run_test = st.button("? Quick Test (3 steps)")

    steps = None
    if run_full:
        steps = 10
    elif run_test:
        steps = 3

    if steps:
        with st.spinner(f"Running {steps}-step AI simulation..."):
            runner = SimulationRunner()
            # Apply user-defined initial state
            runner.ceo_task.revenue = revenue
            runner.ceo_task.users = users
            runner.cfo_task.cash = cash
            runner.cfo_task.burn_rate = burn_rate
            runner.cfo_task.expenses = expenses

            results = runner.run_simulation(steps)
            final_scores = runner.get_final_scores(results)

        st.session_state.simulation_results = {
            "results": results,
            "final_scores": final_scores,
        }
        st.success(f"Simulation complete! {steps} steps run.")

    if st.session_state.simulation_results and st.session_state.simulation_results.get("results"):
        _display_simulation_results()


def _display_simulation_results():
    data = st.session_state.simulation_results
    results = data["results"]
    scores = data["final_scores"]

    st.divider()
    st.header("?? Results")

    col1, col2, col3 = st.columns(3)
    col1.metric("?? CEO Score", f"{scores['ceo']:.3f}")
    col2.metric("?? CFO Score", f"{scores['cfo']:.3f}")
    col3.metric("?? CTO Score", f"{scores['cto']:.3f}")

    # Trend charts
    st.subheader("📈 Performance Trends")
    c1, c2 = st.columns(2)
    c1.markdown("**Revenue**")
    c1.line_chart([s["ceo"]["state"]["revenue"] for s in results])
    c2.markdown("**Cash**")
    c2.line_chart([s["cfo"]["state"]["cash"] for s in results])

    # Company health
    health = []
    for s in results:
        rev_h = min(s["ceo"]["state"]["revenue"] / 5000, 1.0)
        cash_h = min(s["cfo"]["state"]["cash"] / 10000, 1.0)
        health.append(round(rev_h * 0.5 + cash_h * 0.5, 3))

    st.subheader("?? Company Health Over Time")
    st.line_chart(health)

    # Step breakdown
    st.subheader("?? Decision Breakdown")
    for i, step in enumerate(results):
        with st.expander(f"Step {i + 1}"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**?? CEO**")
                st.write(f"Action: {step['ceo']['action']}")
                st.write(f"Reason: {step['ceo'].get('reason', '�')}")
                st.write(f"Reward: {step['ceo']['reward']:.2f}")
            with c2:
                st.markdown("**?? CFO**")
                st.write(f"Action: {step['cfo']['action']}")
                st.write(f"Reason: {step['cfo'].get('reason', '�')}")
                st.write(f"Reward: {step['cfo']['reward']:.2f}")
            with c3:
                st.markdown("**?? CTO**")
                st.write(f"Action: {step['cto']['action']}")
                st.write(f"Reason: {step['cto'].get('reason', '�')}")
                st.write(f"Reward: {step['cto']['reward']:.2f}")


# ------------------------------------------------------------------------------
# TAB 2: STRATEGY ADVISOR (the section that was broken)
# TAB 2: STRATEGY ADVISOR
# ------------------------------------------------------------------------------
def strategy_tab(user_id: int):
    st.header("🎯 One-Click Strategy Generator")
    st.caption("Describe your business problem — Groq will generate a full strategic playbook")

    c1, c2 = st.columns(2)
    with c1:
        user_role = st.selectbox("Your Role", ["CEO", "CFO", "CTO"], key="strategy_user_role")
    with c2:
        agent_role = st.selectbox("Advisor Role", ["CEO", "CFO", "CTO"], index=1, key="strategy_agent_role")
        
    user_problem = st.text_area("Describe your problem in detail", height=120, key="strategy_problem")

    if st.button("🧭 Generate Strategy", key="gen_strategy"):
        if not user_problem.strip():
            st.warning("Please describe your problem first.")
            return

        with st.spinner("Step 1/3 — Diagnosing problem and generating strategies..."):
            base_prompt = f"""You are an elite {agent_role} strategist advising the {user_role}.

Problem:
{user_problem}

Generate:

STEP 1: CORE PROBLEM
(Exactly 3 lines diagnosing the real issue)

STEP 2: STRATEGIES
Give EXACTLY 3 strategies. For each: a bold name and 2-sentence description."""

            part1 = call_ai(base_prompt)

        st.markdown("### 🔍 Problem Diagnosis & Strategies")
        st.markdown(part1)
        st.divider()

        with st.spinner("Step 2/3 — Comparing strategies..."):
            comparison_prompt = f"""Problem: {user_problem}

Strategies identified:
{part1}

Now generate:

STEP 3: COMPARISON TABLE

For EACH of the 3 strategies list:
* 2 pros
* 2 cons  
* Risk level: Low / Medium / High

Be specific — no generic answers."""

            part2 = call_ai(comparison_prompt)

        st.markdown("### ⚖️ Strategy Comparison")
        st.markdown(part2)
        st.divider()

        with st.spinner("Step 3/3 — Building final recommendation..."):
            final_prompt = f"""Problem: {user_problem}

Strategies & Comparison:
{part1}
{part2}

Now generate:

STEP 4: BEST DECISION
Pick ONE strategy. Explain WHY in 3 sentences.

STEP 5: EXECUTION PLAN
Give exactly 5 numbered concrete steps to execute this decision.

STEP 6: RISKS TO WATCH
List exactly 3 risks with a mitigation for each.

Be decisive, sharp, and non-generic."""

            part3 = call_ai(final_prompt)

        st.markdown("## 🚀 Final Recommendation")
        st.divider()

        # Parse and render steps 4, 5, 6
        sections = {"STEP 4": "", "STEP 5": "", "STEP 6": ""}
        current = None
        for line in part3.splitlines():
            for key in sections:
                if key in line:
                    current = key
                    break
            else:
                if current:
                    sections[current] += line + "\n"

        render_step("✅ Best Decision", sections["STEP 4"].strip() or part3[:400])
        render_step("📋 Execution Plan", sections["STEP 5"].strip())
        render_step("⚠️ Risks & Mitigations", sections["STEP 6"].strip())

        if not sections["STEP 5"]:
            # Fallback: just render the whole thing
            st.markdown(part3)

        # Save to chat history so it persists
        save_chat(user_id, "assistant", f"[Strategy from {agent_role} for {user_role}]\n{part1}\n{part2}\n{part3}")


# ------------------------------------------------------------------------------
# TAB 3: AI CHAT
# ------------------------------------------------------------------------------
def chat_tab(user_id: int):
    st.header("💬 AI Executive Advisor")

    chat_manager = None

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        user_role = st.selectbox("Your Role", ["CEO", "CFO", "CTO"], key="chat_user_role")
    with col2:
        agent_role = st.selectbox("Advisor Role", ["CEO", "CFO", "CTO"], index=1, key="chat_agent_role")
    with col3:
        mode = st.selectbox("Mode", ["⚡ Quick", "🧠 Strategist"], key="chat_mode")

    # Display history
    for msg in st.session_state.chat_history:
        r = msg.get("role", "user")
        c = msg.get("content", "")
        st.chat_message(r).markdown(c)

    # Input
    user_input = st.chat_input("Ask your business question...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        save_chat(user_id, "user", user_input)
        st.chat_message("user").markdown(user_input)

        with st.spinner("Thinking..."):
            prompt = build_conversation_prompt(st.session_state.chat_history, user_role, agent_role, mode)
            response = call_ai(prompt)

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        save_chat(user_id, "assistant", response)
        st.chat_message("assistant").markdown(response)
        st.rerun()

    # Strategist refinement
    if mode == "?? Strategist" and st.session_state.chat_history:
        st.divider()
        follow_up = st.text_area("Add context or answer follow-up questions:", key="follow_up_area")
        if st.button("?? Refine Strategy") and follow_up:
            st.session_state.chat_history.append({"role": "user", "content": follow_up})
            save_chat(user_id, "user", follow_up)

            refine_prompt = (
                f"You are a {agent_role} strategist advising the {user_role}.\n\n"
                f"Additional context: {follow_up}\n\n"
                "STEP 4: BEST STRATEGY � pick one\n"
                "STEP 5: EXECUTION PLAN � step by step\n"
                "STEP 6: RISKS � list 3\n\n"
                "Be decisive and practical."
            )
            final = call_ai(refine_prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": final})
            save_chat(user_id, "assistant", final)
            st.markdown("### Refined Strategy")
            st.markdown(final)

    if st.button("?? Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()


# ------------------------------------------------------------------------------
# TAB 4: ANALYTICS
# ------------------------------------------------------------------------------
def analytics_tab():
    st.header("?? Analytics Dashboard")

    if not st.session_state.simulation_results or not st.session_state.simulation_results.get("results"):
        st.info("Run a simulation first to see analytics here.")
        return

    data = st.session_state.simulation_results
    results = data["results"]
    scores = data["final_scores"]

    st.subheader("?? Performance Overview")
    c1, c2, c3, c4 = st.columns(4)
    avg_ceo = sum(s["ceo"]["score"] for s in results) / len(results)
    avg_cfo = sum(s["cfo"]["score"] for s in results) / len(results)
    avg_cto = sum(s["cto"]["score"] for s in results) / len(results)
    overall = (scores["ceo"] + scores["cfo"] + scores["cto"]) / 3
    c1.metric("Avg CEO Score", f"{avg_ceo:.3f}")
    c2.metric("Avg CFO Score", f"{avg_cfo:.3f}")
    c3.metric("Avg CTO Score", f"{avg_cto:.3f}")
    c4.metric("Overall Score", f"{overall:.3f}")

    st.subheader("?? Decision Patterns")
    c1, c2, c3 = st.columns(3)

    for col, role_key, label in [(c1, "ceo", "?? CEO"), (c2, "cfo", "?? CFO"), (c3, "cto", "?? CTO")]:
        actions = [s[role_key]["action"] for s in results]
        counts = {}
        for a in actions:
            counts[a] = counts.get(a, 0) + 1
        col.markdown(f"**{label} Actions**")
        for action, count in sorted(counts.items(), key=lambda x: -x[1]):
            col.write(f"{action}: {count}x")

    st.subheader("?? Score Progression")
    import pandas as pd
    score_data = pd.DataFrame({
        "CEO": [s["ceo"]["score"] for s in results],
        "CFO": [s["cfo"]["score"] for s in results],
        "CTO": [s["cto"]["score"] for s in results],
    })
    st.line_chart(score_data)


# ------------------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------------------
if not st.session_state.user:
    login_page()
else:
    main_app()
