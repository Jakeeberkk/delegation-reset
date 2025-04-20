
import streamlit as st
from difflib import SequenceMatcher
import pandas as pd

st.set_page_config(page_title="Delegation Assistant", layout="wide")

# Header
st.markdown(
    "<h1 style='text-align: left; color: white; background-color: black; padding: 10px 20px; border-radius: 8px;'>"
    "🧠 Delegation Assistant <span style='font-size: 16px; font-weight: normal;'>&nbsp;by Expedited Entrepreneur</span>"
    "</h1>", unsafe_allow_html=True)

# Styling
st.markdown("""
<style>
.card {
    background-color: #f9f9f9;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.category-pill {
    display: inline-block;
    padding: 2px 10px;
    font-size: 12px;
    border-radius: 12px;
    margin-left: 8px;
    color: white;
}
.Admin { background-color: #888; }
.Sales { background-color: #007bff; }
.Creative { background-color: #e83e8c; }
.Technical { background-color: #6610f2; }
.Logistics { background-color: #fd7e14; }
.Finance { background-color: #28a745; }
.CustomerService { background-color: #17a2b8; }
</style>
""", unsafe_allow_html=True)

# Constants
categories = ["Admin", "Sales", "Creative", "Technical", "Logistics", "Finance", "Customer Service"]
software_library = {
    "HubSpot": ["crm", "email automation", "lead tracking", "contact management"],
    "Monday.com": ["project management", "task tracking", "workflow automation"],
    "GoHighLevel": ["crm", "funnels", "sms automation", "lead capture"],
    "Slack": ["team communication", "messaging", "channel updates"],
    "Google Sheets": ["data entry", "spreadsheet", "reporting", "analysis"]
}

# Default strengths/weaknesses
default_strengths = ["CRM usage", "Email writing", "Scheduling", "Data entry", "Project management", "Lead generation"]
default_weaknesses = ["Avoids phone calls", "Poor time management", "Dislikes spreadsheets", "Overthinks tasks"]

# Session state
for key in ["employees", "tools", "tasks", "delegation_history"]:
    if key not in st.session_state:
        st.session_state[key] = []

# Sidebar
st.sidebar.title("Controls")
if st.sidebar.button("Clear Employees"): st.session_state.employees = []
if st.sidebar.button("Clear Tools"): st.session_state.tools = []
if st.sidebar.button("Clear Tasks"): st.session_state.tasks = []
if st.sidebar.button("Reset Everything"):
    for key in st.session_state:
        st.session_state[key] = []
    st.sidebar.info("All data cleared. Please refresh the page.")

# Section 1: Add Employee
st.header("1. Add Employee")
with st.form("employee_form"):
    name = st.text_input("Employee Name")
    role = st.text_input("Role")
    strengths = st.multiselect("Strengths", default_strengths)
    custom_strength = st.text_input("Custom Strength (optional)")
    weaknesses = st.multiselect("Weaknesses", default_weaknesses)
    custom_weakness = st.text_input("Custom Weakness (optional)")
    if st.form_submit_button("Add Employee") and name:
        all_strengths = strengths + ([custom_strength] if custom_strength else [])
        all_weaknesses = weaknesses + ([custom_weakness] if custom_weakness else [])
        st.session_state.employees.append({
            "name": name,
            "role": role,
            "strengths": [s.strip().lower() for s in all_strengths],
            "weaknesses": [w.strip().lower() for w in all_weaknesses]
        })
        st.success(f"Added employee: {name}")

# Section 2: Add Software Tool
st.header("2. Add Software Tool")
with st.form("tool_form"):
    tool_name = st.selectbox("Tool", list(software_library.keys()))
    if st.form_submit_button("Add Tool"):
        if tool_name not in [t["name"] for t in st.session_state.tools]:
            st.session_state.tools.append({
                "name": tool_name,
                "capabilities": software_library[tool_name]
            })
            st.success(f"Added tool: {tool_name}")
        else:
            st.warning(f"{tool_name} is already added.")

# Section 3: Add Task
st.header("3. Add Task")
with st.form("task_form"):
    task_desc = st.text_input("Task Description")
    task_time = st.number_input("Time Spent (minutes)", min_value=1, step=1)
    task_category = st.selectbox("Category", categories)
    delegatable = st.radio("Is this delegatable?", ("Yes", "No"))
    if st.form_submit_button("Add Task") and task_desc:
        st.session_state.tasks.append({
            "description": task_desc.strip(),
            "time_spent": task_time,
            "category": task_category,
            "delegatable": delegatable == "Yes"
        })
        st.success(f"Added task: {task_desc}")

# Card rendering
def display_card(title, lines):
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{title}**")
    for line in lines:
        st.markdown(line)
    st.markdown("</div>", unsafe_allow_html=True)

# Current data
if st.session_state.employees:
    st.subheader("Current Employees")
    for emp in st.session_state.employees:
        lines = [f"**Role:** {emp['role']}", "**Strengths:**"] +                 [f"- {s.title()}" for s in emp["strengths"]]
        if emp["weaknesses"]:
            lines += ["**Weaknesses:**"] + [f"- {w.title()}" for w in emp["weaknesses"]]
        display_card(emp['name'], lines)

if st.session_state.tools:
    st.subheader("Current Tools")
    for tool in st.session_state.tools:
        lines = ["**Capabilities:**"] + [f"- {cap.title()}" for cap in tool["capabilities"]]
        display_card(tool['name'], lines)

if st.session_state.tasks:
    st.subheader("Current Tasks")
    for task in st.session_state.tasks:
        lines = [
            f"**Time:** {task['time_spent']} mins",
            f"**Category:** {task['category']}",
            f"**Delegatable:** {task['delegatable']}"
        ]
        display_card(task["description"], lines)

# Matching logic
def get_similarity(text1, text2):
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def find_best_match(task_desc):
    match_pool = []
    for emp in st.session_state.employees:
        score = max((get_similarity(task_desc, s) for s in emp["strengths"]), default=0)
        match_pool.append(("employee", emp["name"], emp.get("role", ""), score))

    for tool in st.session_state.tools:
        score = max((get_similarity(task_desc, cap) for cap in tool["capabilities"]), default=0)
        match_pool.append(("tool", tool["name"], "", score))

    match_pool.sort(key=lambda x: x[3], reverse=True)
    return match_pool[:2]

# Section 4: Run Match
st.header("4. Run Delegation Match")
if st.button("Run Match"):
    st.session_state.delegation_history.clear()
    for task in st.session_state.tasks:
        if task["delegatable"]:
            results = find_best_match(task["description"])
            if results:
                primary = results[0]
                target = f"{primary[1]} ({primary[2]})" if primary[0] == "employee" else f"Tool: {primary[1]}"
                st.success(f"'{task['description']}' → {target} – Confidence: {round(primary[3]*100)}%")
                st.session_state.delegation_history.append({
                    "Task": task["description"],
                    "Delegated To": primary[1],
                    "Type": primary[0],
                    "Confidence": f"{round(primary[3]*100)}%"
                })
            else:
                st.warning(f"No strong match for: {task['description']}")
        else:
            st.info(f"'{task['description']}' is not marked for delegation.")

# Export History
if st.session_state.delegation_history:
    st.subheader("📚 Delegation History")
    df = pd.DataFrame(st.session_state.delegation_history)
    st.dataframe(df)
    st.download_button("📥 Download History", df.to_csv(index=False), "delegation_history.csv", "text/csv")
