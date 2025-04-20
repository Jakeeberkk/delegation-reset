
import streamlit as st
from difflib import SequenceMatcher
import pandas as pd

st.set_page_config(page_title="Delegation Assistant", layout="wide")

# Header
st.markdown(
    "<h1 style='text-align: left; color: white; background-color: black; padding: 10px 20px; border-radius: 8px;'>"
    "🧠 Delegation Assistant <span style='font-size: 16px; font-weight: normal;'>&nbsp;by Expedited Entrepreneur</span>"
    "</h1>", unsafe_allow_html=True)

# CSS styles
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
default_strengths = ["CRM usage", "Email writing", "Scheduling", "Data entry", "Project management", "Lead generation"]
default_weaknesses = ["Avoids phone calls", "Poor time management", "Dislikes spreadsheets", "Overthinks tasks"]

# Built-in software tools and their capabilities
software_library = {
    "HubSpot": ["crm", "email automation", "lead tracking", "contact management"],
    "Monday.com": ["project management", "task tracking", "workflow automation"],
    "GoHighLevel": ["crm", "funnels", "sms automation", "lead capture"],
    "Slack": ["team communication", "messaging", "channel updates"],
    "Google Sheets": ["data entry", "spreadsheet", "reporting", "analysis"]
}

# State
if "employees" not in st.session_state:
    st.session_state.employees = []
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "tools" not in st.session_state:
    st.session_state.tools = []
if "delegation_history" not in st.session_state:
    st.session_state.delegation_history = []

# Sidebar controls
st.sidebar.title("Controls")
if st.sidebar.button("Clear Employees"):
    st.session_state.employees = []
if st.sidebar.button("Clear Tasks"):
    st.session_state.tasks = []
if st.sidebar.button("Clear Tools"):
    st.session_state.tools = []
if st.sidebar.button("Reset Everything"):
    st.session_state.employees = []
    st.session_state.tasks = []
    st.session_state.tools = []
    st.session_state.delegation_history = []
    st.sidebar.info("All data cleared. Please refresh the page.")

# Add Employee
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

# Add Tool
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

# Add Task
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

# Display Current Data
def display_card(title, lines):
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{title}**")
    for line in lines:
        st.markdown(line)
    st.markdown("</div>", unsafe_allow_html=True)

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

# Matching Logic
def get_similarity(text1, text2):
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def find_best_match(task_desc):
    match_pool = []

    # Match to employees
    for emp in st.session_state.employees:
        score = 0
        for s in emp["strengths"]:
            score = max(score, get_similarity(task_desc, s))
        match_pool.append(("employee", emp["name"], emp.get("role", ""), score))

    # Match to tools
    for tool in st.session_state.tools:
        score = 0
        for cap in tool["capabilities"]:
            score = max(score, get_similarity(task_desc, cap))
        match_pool.append(("tool", tool["name"], "", score))

    match_pool.sort(key=lambda x: x[3], reverse=True)
    return match_pool[:2]

# Run Matching
st.header("4. Run Delegation Match")
if st.button("Run Match"):
    st.session_state.delegation_history.clear()
    for task in st.session_state.tasks:
        if task["delegatable"]:
            results = find_best_match(task["description"])
            if results:
                primary = results[0]
                if primary[0] == "employee":
                    st.success(f"'{task['description']}' → {primary[1]} ({primary[2]}) – Confidence: {round(primary[3]*100)}%")
                else:
                    st.success(f"'{task['description']}' → Tool: {primary[1]} – Confidence: {round(primary[3]*100)}%")

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
