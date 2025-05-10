import streamlit as st
import json

# Load questions from JSON
@st.cache_data
def load_questions(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Scoring logic
def evaluate_answers(questions, user_answers):
    score = 0
    correct_count = 0
    incorrect_count = 0
    results = []

    for idx, q in enumerate(questions):
        correct = q["answer"]
        user = user_answers.get(idx)

        if isinstance(correct, str):
            correct_set = set(a.strip().upper() for a in correct.split(","))
        else:
            correct_set = set(correct)

        user_set = set(user) if isinstance(user, list) else {user} if user else set()

        if user_set == correct_set:
            score += 1
            correct_count += 1
            results.append(("✅", q["question"], user_set, correct_set))
        else:
            score -= 1
            incorrect_count += 1
            results.append(("❌", q["question"], user_set, correct_set))

    return score, correct_count, incorrect_count, results

# Main app
def main():
    st.set_page_config(page_title="LLM Quiz", layout="wide")
    st.title("🧠 Databricks Generative AI Engineering Associate - Practice Quiz")

    questions = load_questions("./normalized_mcqs.json")
    user_answers = {}

    st.markdown("### Answer the following questions:")

    for idx, q in enumerate(questions):
        st.markdown(f"**Q{idx+1}: {q['question']}**")

        options = q["options"]
        qtype = q.get("question_type", "mcq")

        formatted_options = [f"{key}: {val}" for key, val in options.items()]
        key_to_option = {f"{key}: {val}": key for key, val in options.items()}

        if qtype == "mcq":
            selected = st.radio(
                "Choose one:",
                options=formatted_options,
                key=f"q_{idx}",
                index=None  # No default selection
            )
            user_answers[idx] = key_to_option[selected] if selected else None

        elif qtype == "more_than_one_correct":
            selected_list = st.multiselect(
                "Choose one or more:",
                options=formatted_options,
                key=f"q_{idx}"
            )
            user_answers[idx] = [key_to_option[s] for s in selected_list] if selected_list else []

        st.markdown("---")

    if st.button("Submit Quiz"):
        score, correct, incorrect, results = evaluate_answers(questions, user_answers)

        st.success(f"🎯 Final Score: {score}")
        st.info(f"✅ Correct Answers: {correct} | ❌ Incorrect Answers: {incorrect}")

        st.markdown("### 📋 Review")
        for icon, question, user_ans, correct_ans in results:
            st.markdown(f"{icon} **{question}**")
            st.markdown(f"- Your answer: `{', '.join(user_ans) if user_ans else 'No answer'}`")
            st.markdown(f"- Correct answer: `{', '.join(correct_ans)}`")
            st.markdown("---")

if __name__ == "__main__":
    main()