
import streamlit as st
from difflib import SequenceMatcher
import pandas as pd

st.set_page_config(page_title="Delegation Assistant", layout="wide")

# Logo and header
st.image("https://raw.githubusercontent.com/Jakeeberkk/branding-assets/main/expedited-entrepreneur-logo.png", width=200)
st.title("Delegation Assistant Tool")

# --- Constants ---
default_strengths = [
    "Task prioritization", "Calendar & meeting management", "CRM usage", "Invoicing & payment follow-up",
    "Vendor communication", "Managing inbox", "Taking notes during meetings", "Creating SOPs",
    "Spreadsheet building", "Data cleanup", "Travel booking", "Project tracking", "Social media scheduling",
    "Customer follow-up", "Cold calling", "Warm lead nurturing", "Quote generation", "Order processing",
    "Inventory tracking", "Creating reports", "Writing professional emails", "Problem-solving under pressure",
    "Cross-functional coordination", "File and folder organization", "Research & summarizing information"
]

default_weaknesses = [
    "Easily overwhelmed with multi-tasking", "Avoids confrontation or client follow-up", "Not detail-oriented",
    "Struggles with written communication", "Doesn’t enjoy phone calls", "Gets distracted easily",
    "Avoids complex spreadsheets or numbers", "Uncomfortable with tech tools or new software",
    "Poor time estimation", "Doesn’t take initiative", "Slow response time", "Struggles with follow-through",
    "Disorganized digital workspace", "Doesn’t document processes", "Uncomfortable giving or receiving feedback"
]

category_colors = {
    "Admin": "#e0e0e0",
    "Sales": "#d0e8ff",
    "Creative": "#fddde6",
    "Technical": "#e6f2ff",
    "Logistics": "#fff3cd",
    "Finance": "#e2f0cb",
    "Customer Service": "#fdebd0"
}

# --- Session State ---
if "employees" not in st.session_state:
    st.session_state.employees = []
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "delegation_history" not in st.session_state:
    st.session_state.delegation_history = []

# --- Sidebar Controls ---
st.sidebar.title("Controls")
if st.sidebar.button("Clear Employees"):
    st.session_state.employees = []
if st.sidebar.button("Clear Tasks"):
    st.session_state.tasks = []
if st.sidebar.button("Reset Everything"):
    st.session_state.employees = []
    st.session_state.tasks = []
    st.session_state.delegation_history = []
    st.sidebar.info("Data cleared. Please refresh the page.")

# --- Employee Form ---
st.header("1. Add Employee")
with st.form("employee_form"):
    name = st.text_input("Name")
    role = st.text_input("Role")
    strengths = st.multiselect("Strengths", default_strengths)
    ratings = {s: st.slider(f"Skill Level for '{s}'", 1, 5, 5) for s in strengths}
    custom_strength = st.text_input("Custom Strength (optional)")
    weaknesses = st.multiselect("Weaknesses", default_weaknesses)
    custom_weakness = st.text_input("Custom Weakness (optional)")
    submitted = st.form_submit_button("Add Employee")

    if submitted and name:
        all_strengths = strengths + ([custom_strength] if custom_strength else [])
        all_weaknesses = weaknesses + ([custom_weakness] if custom_weakness else [])
        st.session_state.employees.append({
            "name": name,
            "role": role,
            "strengths": {s.strip().lower(): ratings.get(s, 5) for s in all_strengths},
            "weaknesses": [w.strip().lower() for w in all_weaknesses]
        })
        st.success(f"Added employee: {name}")

# --- Display Employees in Card Style ---
if st.session_state.employees:
    st.subheader("Current Employees")
    for emp in st.session_state.employees:
        with st.container():
            st.markdown(f"**{emp['name']}** – {emp['role']}")
            st.markdown("**Strengths:**")
            for s, r in emp["strengths"].items():
                st.markdown(f"- {s.title()} (Skill: {r}/5)")
            if emp["weaknesses"]:
                st.markdown("**Weaknesses:**")
                for w in emp["weaknesses"]:
                    st.markdown(f"- {w.title()}")
            st.markdown("---")

# --- Export Employees ---
def convert_employees_to_csv():
    data = []
    for emp in st.session_state.employees:
        strength_str = "; ".join([f"{k}:{v}" for k, v in emp["strengths"].items()])
        weakness_str = "; ".join(emp["weaknesses"])
        data.append({
            "name": emp["name"],
            "role": emp["role"],
            "strengths": strength_str,
            "weaknesses": weakness_str
        })
    return pd.DataFrame(data).to_csv(index=False)

if st.session_state.employees:
    st.download_button(
        label="📤 Download Employee List (CSV)",
        data=convert_employees_to_csv(),
        file_name="employee_list.csv",
        mime="text/csv"
    )

# --- Task Input ---
st.header("2. Add Task")
with st.form("task_form"):
    task_desc = st.text_input("Task Description")
    task_time = st.number_input("Time Spent (in minutes)", min_value=1, step=1)
    task_category = st.selectbox("Category", list(category_colors.keys()))
    delegatable = st.radio("Would you like to delegate this task?", ("Yes", "No"))
    task_submitted = st.form_submit_button("Add Task")

    if task_submitted and task_desc:
        st.session_state.tasks.append({
            "description": task_desc.strip(),
            "time_spent": task_time,
            "category": task_category,
            "delegatable": delegatable == "Yes"
        })
        st.success(f"Added task: {task_desc}")

# --- Display Tasks as Cards ---
if st.session_state.tasks:
    st.subheader("Current Tasks")
    for task in st.session_state.tasks:
        bg = category_colors.get(task["category"], "#f0f0f0")
        st.markdown(
            f"<div style='background-color:{bg}; padding: 12px; border-radius: 8px; margin-bottom: 10px;'>"
            f"<strong>{task['description']}</strong><br>"
            f"<em>Time:</em> {task['time_spent']} mins<br>"
            f"<em>Category:</em> {task['category']}<br>"
            f"<em>Delegatable:</em> {task['delegatable']}</div>",
            unsafe_allow_html=True
        )

# --- Matching Logic ---
def get_similarity(task_desc, strength):
    return SequenceMatcher(None, task_desc.lower(), strength).ratio()

def find_best_match(task_desc, employees):
    emp_scores = {}
    for emp in employees:
        score = 0
        for s, rating in emp["strengths"].items():
            similarity = get_similarity(task_desc, s)
            weighted_score = similarity * (rating / 5)
            score = max(score, weighted_score)
        emp_scores[emp["name"]] = (emp, score)

    sorted_scores = sorted(emp_scores.values(), key=lambda x: x[1], reverse=True)
    best_match = sorted_scores[0][0] if sorted_scores and sorted_scores[0][1] > 0.4 else None
    best_score = sorted_scores[0][1] if sorted_scores else 0
    return best_match, best_score

# --- Run Delegation Match ---
st.header("3. Run Delegation Match")
if st.button("Run Match"):
    st.session_state.delegation_history.clear()
    for task in st.session_state.tasks:
        if task["delegatable"]:
            match, score = find_best_match(task["description"], st.session_state.employees)
            if match:
                st.success(f"'{task['description']}' → {match['name']} – Confidence: {round(score * 100)}%")
                st.session_state.delegation_history.append({
                    "Task": task["description"],
                    "Assigned To": match["name"],
                    "Confidence": f"{round(score * 100)}%"
                })
            else:
                st.warning(f"No strong match for: {task['description']}")
        else:
            st.info(f"'{task['description']}' is not marked for delegation.")

# --- Delegation History Log ---
if st.session_state.delegation_history:
    st.subheader("📚 Delegation History Log")
    df_history = pd.DataFrame(st.session_state.delegation_history)
    st.dataframe(df_history)
    csv = df_history.to_csv(index=False)
    st.download_button(
        label="📥 Download Delegation History",
        data=csv,
        file_name="delegation_history.csv",
        mime="text/csv"
    )
