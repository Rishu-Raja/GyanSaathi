
import streamlit as st

from database import (
    create_database,
    save_student,
    save_learning_history,
    get_learning_history
)

from prompts import (
    create_personalized_prompt,
    create_few_shot_prompt,
    create_structured_prompt
)

from ai_engine import generate_response

create_database()

st.set_page_config(
    page_title="AI Personalized Learning Assistant",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 AI GyanSaathi")
st.write("AI Personalized Learning Assistant")

# Student profile
st.sidebar.header("Student Profile")

name = st.sidebar.text_input("Your Name")

level = st.sidebar.selectbox(
    "Knowledge Level",
    ["Beginner", "Intermediate", "Advanced"]
)

goal = st.sidebar.selectbox(
    "Learning Goal",
    [
        "Understand Concepts",
        "Exam Preparation",
        "Interview Preparation",
        "Revision"
    ]
)

learning_style = st.sidebar.selectbox(
    "Learning Style",
    [
        "Step-by-Step",
        "Simple Explanation",
        "Practical Examples"
    ]
)

if "student_id" not in st.session_state:
    st.session_state.student_id = None

if st.sidebar.button("Save Profile"):
    if name.strip():
        st.session_state.student_id = save_student(
            name.strip(), level, goal, learning_style
        )
        st.sidebar.success("Profile saved!")
    else:
        st.sidebar.warning("Please enter your name.")

# Navigation
page = st.sidebar.radio(
    "Menu",
    ["Learn", "Prompt Lab", "Study Planner", "Learning History"]
)


def generate_lesson(subject, topic, technique):

    if not subject.strip() or not topic.strip():
        st.warning("Enter a subject and topic.")
        return

    if st.session_state.student_id is None:
        st.warning("Save your student profile first.")
        return

    if technique == "Personalized":
        prompt = create_personalized_prompt(
            name, subject, topic, level, goal, learning_style
        )

    elif technique == "Few-Shot":
        prompt = create_few_shot_prompt(
            subject, topic, level, goal
        )

    else:
        prompt = create_structured_prompt(
            subject, topic, level, goal
        )

    with st.spinner("Gemini is preparing your lesson..."):
        answer = generate_response(prompt)

    if answer.startswith("Gemini API Error:"):
        st.error(answer)
        return

    save_learning_history(
        st.session_state.student_id,
        subject,
        topic,
        technique,
        prompt,
        answer
    )

    st.markdown(answer)


if page == "Learn":

    st.header("📚 Learn a Topic")

    subject = st.text_input("Subject", "Python")
    topic = st.text_input("Topic", "Functions")

    if st.button("Generate Lesson"):
        generate_lesson(subject, topic, "Personalized")


elif page == "Prompt Lab":

    st.header("🧪 Prompt Engineering Lab")
    st.write("Compare different prompting techniques.")

    subject = st.text_input("Subject", "Python")
    topic = st.text_input("Topic", "Loops")

    technique = st.selectbox(
        "Prompting Technique",
        ["Personalized", "Few-Shot", "Structured"]
    )

    if st.button("Run Prompt"):
        generate_lesson(subject, topic, technique)


elif page == "Study Planner":

    st.header("🎯 Study Plan Generator")

    subject = st.text_input("Subject", "Data Structures")
    days = st.number_input(
        "Number of Days", min_value=1, max_value=90, value=7
    )
    hours = st.number_input(
        "Study Hours per Day", min_value=1, max_value=12, value=2
    )

    if st.button("Generate Study Plan"):

        if st.session_state.student_id is None:
            st.warning("Save your student profile first.")
        else:
            prompt = f"""
            You are an expert study planner.

            Student level: {level}
            Learning goal: {goal}
            Subject: {subject}
            Duration: {days} days
            Available time: {hours} hours per day

            Create a practical day-by-day study plan.
            Include topics, practice, revision, and breaks.
            Use simple language and a clear structure.
            """

            with st.spinner("Creating your study plan..."):
                answer = generate_response(prompt)

            if answer.startswith("Gemini API Error:"):
                st.error(answer)
            else:
                st.markdown(answer)

                save_learning_history(
                    st.session_state.student_id,
                    subject,
                    f"{days}-day study plan",
                    "Study Planner",
                    prompt,
                    answer
                )


elif page == "Learning History":

    st.header("📊 Learning History")

    if st.session_state.student_id is None:
        st.info("Save your student profile first.")
    else:
        records = get_learning_history(
            st.session_state.student_id
        )

        if records:
            st.dataframe(
                records,
                column_config=None,
                use_container_width=True
            )
        else:
            st.info("No learning history yet.")


# Footer
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #0e1117;
        color: #b0b0b0;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        border-top: 1px solid #303030;
        z-index: 999;
    }
    </style>

    <div class="footer">
        Developed by <strong>Rishu Raja</strong>
    </div>
    """,
    unsafe_allow_html=True
)
