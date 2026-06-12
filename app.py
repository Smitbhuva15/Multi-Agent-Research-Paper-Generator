from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from agents.supervisor import run_pipeline

load_dotenv()

st.set_page_config(
    page_title="Multi-Agent Research Paper Generator",
    page_icon="📄",
    layout="wide",
)

st.title("Multi-Agent Research Paper Generator")
st.caption("Supervisor -> Researcher -> Writer -> Critic -> Editor")

if not os.getenv("GROQ_API_KEY"):
    st.error("Missing GROQ_API_KEY. Add it in .env before generating papers.")

st.write("Enter a topic and generate a full markdown research paper.")
topic = st.text_area(
    "Research Topic",
    placeholder="Example: Multi-agent coordination for disaster response",
    height=90,
)

generate_clicked = st.button("Generate Paper", type="primary", use_container_width=True)

if generate_clicked:
    if not topic.strip():
        st.warning("Please enter a topic.")
        st.stop()

    if not os.getenv("GROQ_API_KEY"):
        st.stop()

    status_box = st.empty()

    def on_stage(stage: str, message: str) -> None:
        status_box.info(f"{stage}: {message}")

    try:
        with st.spinner("Running multi-agent pipeline..."):
            state = run_pipeline(topic=topic, stage_callback=on_stage)
    except Exception as exc:
        status_box.empty()
        st.error(f"Pipeline failed: {exc}")
        st.stop()

    status_box.success("Pipeline complete.")

    st.subheader("Research Sources")
    source_rows = []
    for index, source in enumerate(state.research.sources, start=1):
        source_rows.append(
            {
                "Source ID": f"S{index}",
                "Title": source.title,
                "URL": source.url,
                "Snippet": source.snippet,
            }
        )

    st.dataframe(source_rows, use_container_width=True, hide_index=True)

    st.subheader("Critic Review")
    score_col, weak_col, improve_col = st.columns([1, 2, 2])
    score_col.metric("Score", f"{state.review.score}/10")

    with weak_col:
        st.markdown("**Weaknesses**")
        for item in state.review.weaknesses:
            st.write(f"- {item}")

    with improve_col:
        st.markdown("**Improvements**")
        for item in state.review.improvements:
            st.write(f"- {item}")

    with st.expander("View Draft Paper"):
        st.markdown(state.draft_paper)

    st.subheader("Final Paper")
    st.markdown(state.final_paper)

    st.download_button(
        label="Download Markdown",
        data=state.final_paper,
        file_name="research_paper.md",
        mime="text/markdown",
        use_container_width=True,
    )
