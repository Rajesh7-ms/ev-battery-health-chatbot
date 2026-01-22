import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import base64

# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="EV Battery Health Chatbot",
    page_icon="🔋",
    layout="wide"
)

# -------------------------------------------------
# Background + CSS Styling
# -------------------------------------------------
def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        /* Full screen background */
        html, body, [data-testid="stApp"] {{
            height: 100%;
            margin: 0;
        }}

        .stApp {{
            background: url("data:image/png;base64,{encoded}") no-repeat center center fixed;
            background-size: cover;
        }}

        /* Remove Streamlit padding */
        .block-container {{
            padding: 0 !important;
            margin: 0 !important;
        }}

        /* Main content panel */
        .content-box {{
            background-color: rgba(0, 0, 0, 0.65);
            padding: 2.5rem;
            border-radius: 18px;
            max-width: 600px;
            margin: 8vh auto;
        }}

        /* Text color fix */
        .content-box h1,
        .content-box h2,
        .content-box h3,
        .content-box p,
        .content-box label {{
            color: #ffffff !important;
        }}

        /* Input width */
        .content-box input {{
            width: 95% !important;
        }}

        /* Send button */
        button[kind="primary"] {{
            background-color: #00ff66 !important;
            color: transparent !important;
            width: 55px;
            height: 55px;
            border-radius: 50%;
            border: none;
        }}

        button[kind="primary"]::after {{
            content: "➤";
            color: black;
            font-size: 22px;
        }}

        button[kind="primary"]:hover::after {{
            content: "Send";
            font-size: 13px;
        }}

        /* REMOVE STREAMLIT HEADER & FOOTER */
        header {{
            visibility: hidden;
        }}

        footer {{
            visibility: hidden;
        }}

        [data-testid="stToolbar"] {{
            display: none;
        }}

        /* REMOVE HEADING ANCHOR GREY BOX */
        a[href^="#"] {{
            background: transparent !important;
            box-shadow: none !important;
        }}

        h1 a, h2 a, h3 a {{
            background: transparent !important;
        }}

        [data-testid="stMarkdownContainer"] a {{
            background: transparent !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# -------------------------------------------------
# Apply background
# -------------------------------------------------
set_background("battery_bg.png")  # image must exist in same folder

# -------------------------------------------------
# Main Content
# -------------------------------------------------
st.markdown("<div class='content-box'>", unsafe_allow_html=True)

st.markdown(
    """
    <h1 style='text-align:center;'>🔋 EV Battery Health Chatbot</h1>
    <p style='text-align:center; font-size:17px;'>
    AI-based assistant for battery health, remaining life, and safety
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# -------------------------------------------------
# Battery Dataset
# -------------------------------------------------
data = {
    "Cycle": [1, 50, 100, 150, 200, 250, 300],
    "Capacity": [2.0, 1.96, 1.92, 1.88, 1.84, 1.80, 1.75]
}
df = pd.DataFrame(data)

# -------------------------------------------------
# ML Model
# -------------------------------------------------
X = df[["Cycle"]]
y = df["Capacity"]

model = LinearRegression()
model.fit(X, y)

# -------------------------------------------------
# SoH & RUL
# -------------------------------------------------
initial_capacity = df["Capacity"].iloc[0]
EOL_capacity = 0.7 * initial_capacity

future_cycles = pd.DataFrame({"Cycle": range(1, 2000)})
future_capacity = model.predict(future_cycles)

for cycle, cap in zip(future_cycles["Cycle"], future_capacity):
    if cap <= EOL_capacity:
        failure_cycle = cycle
        break

current_cycle = df["Cycle"].iloc[-1]
RUL = failure_cycle - current_cycle
SoH = (future_capacity[current_cycle - 1] / initial_capacity) * 100

avg_cycles_per_year = 300
estimated_usage_years = current_cycle / avg_cycles_per_year

# -------------------------------------------------
# Chatbot Logic
# -------------------------------------------------
def battery_chatbot(user_input):
    user_input = user_input.lower()

    if "health" in user_input:
        return f"🔋 Battery State of Health is {SoH:.2f}%."
    elif "life" in user_input or "remaining" in user_input:
        return f"⏳ Remaining Useful Life is approximately {RUL} cycles."
    elif "safe" in user_input:
        return "✅ Battery is safe to use." if SoH > 75 else "⚠️ Battery is aging."
    elif "year" in user_input or "used" in user_input:
        return f"📅 Estimated usage is about {estimated_usage_years:.1f} years."
    else:
        return "💬 Ask about battery health, remaining life, safety, or usage."

# -------------------------------------------------
# Chat UI
# -------------------------------------------------
st.subheader("💬 Ask the Battery Assistant")

user_question = st.text_input("Enter your question")

if st.button("", key="send_button", type="primary"):
    if user_question.strip():
        st.markdown(f"**You:** {user_question}")
        st.markdown(f"**Assistant:** {battery_chatbot(user_question)}")
    else:
        st.warning("Please enter a question.")

st.divider()

with st.expander("📊 Battery Insights"):
    st.write(f"State of Health: {SoH:.2f}%")
    st.write(f"Remaining Useful Life: {RUL} cycles")
    st.write(f"Estimated Usage: {estimated_usage_years:.1f} years")

st.markdown("</div>", unsafe_allow_html=True)
