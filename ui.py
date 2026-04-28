# Run backend first:
#   uvicorn app.main:app --reload
#
# Run UI:
#   streamlit run ui.py

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import requests
from app.utils.audit import audit_response

API_URL = "http://localhost:8000/analyze"

# --- Sample inputs ---
SAMPLES = {
    "Positive Reviews": [
        "Absolutely love this product! Best purchase I've made.",
        "Works perfectly, fast delivery, great quality.",
        "My baby loves it. Would buy again without hesitation.",
        "Five stars. Does exactly what it says. No complaints.",
    ],
    "Negative Reviews": [
        "Terrible quality. Broke after one day.",
        "Complete waste of money. Do not buy.",
        "Returned it immediately. Very disappointed.",
        "Worst product I have ever bought.",
    ],
    "Mixed Reviews": [
        "Good product but shipping was slow.",
        "Quality is decent, price is a bit high.",
        "Works fine for the price, nothing special.",
        "Love the design but the material feels cheap.",
    ],
    "Noisy Input": [
        "asdfghjkl qwerty 12345 !!!???",
        "...",
        "####",
        "BUY NOW!!! CLICK HERE!!!",
    ],
    "Empty Input": [],
}


def call_api(reviews: list[str]) -> dict:
    """POST reviews to the /analyze endpoint."""
    resp = requests.post(API_URL, json={"reviews": reviews}, timeout=60)
    resp.raise_for_status()
    return resp.json()


def sentiment_label(score: float) -> str:
    if score >= 0.6:
        return "Very Positive"
    elif score >= 0.2:
        return "Positive"
    elif score >= -0.2:
        return "Neutral / Mixed"
    elif score >= -0.6:
        return "Negative"
    else:
        return "Very Negative"


def sentiment_color(score: float) -> str:
    if score >= 0.2:
        return "green"
    elif score >= -0.2:
        return "orange"
    else:
        return "red"


def render_verdict(data: dict, reviews: list[str]):
    """Render the full verdict output with audit."""
    st.divider()
    st.subheader("Verdict")

    # Summaries
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Summary (English)**")
        st.info(data.get("summary_en", "—"))
    with col2:
        st.markdown("**Summary (Arabic)**")
        st.info(data.get("summary_ar", "—"))

    # Pros / Cons
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**Pros**")
        pros = data.get("pros", [])
        if pros:
            for p in pros:
                st.markdown(f"✅ {p}")
        else:
            st.caption("None identified")
    with col4:
        st.markdown("**Cons**")
        cons = data.get("cons", [])
        if cons:
            for c in cons:
                st.markdown(f"❌ {c}")
        else:
            st.caption("None identified")

    st.markdown("")

    # Scores
    col5, col6 = st.columns(2)
    sentiment = data.get("sentiment_score", 0)
    confidence = data.get("confidence", 0)

    with col5:
        st.markdown("**Sentiment Score**")
        label = sentiment_label(sentiment)
        color = sentiment_color(sentiment)
        st.markdown(f":{color}[{sentiment:.2f} — {label}]")
        st.progress((sentiment + 1) / 2)

    with col6:
        st.markdown("**Confidence**")
        conf_label = "High" if confidence >= 0.7 else "Medium" if confidence >= 0.4 else "Low"
        conf_color = "green" if confidence >= 0.7 else "orange" if confidence >= 0.4 else "red"
        st.markdown(f":{conf_color}[{confidence:.2f} — {conf_label}]")
        st.progress(confidence)

    # Uncertainty reason
    uncertainty = data.get("uncertainty_reason", "").strip()
    if uncertainty:
        st.warning(f"⚠️ Uncertainty: {uncertainty}")

    # Audit results
    st.divider()
    st.markdown("**Quality Audit**")
    audit = audit_response(data, reviews)
    if audit["valid"]:
        st.success("✅ Output Valid — passed all quality checks")
    else:
        st.error("Quality issues detected:")
        for issue in audit["issues"]:
            st.markdown(f"- ⚠️ {issue}")


# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Moms Verdict AI", page_icon="👶", layout="centered")
st.title("👶 Moms Verdict AI")
st.caption("Paste product reviews to get a structured verdict in English and Arabic.")

# ─── Sample buttons ───────────────────────────────────────────────────────────
st.markdown("**Quick test inputs:**")
cols = st.columns(len(SAMPLES))
for col, (label, reviews) in zip(cols, SAMPLES.items()):
    if col.button(label, use_container_width=True):
        st.session_state["prefill"] = "\n".join(reviews)

# ─── Text area ────────────────────────────────────────────────────────────────
default_text = st.session_state.get("prefill", "")
reviews_input = st.text_area(
    "Reviews (one per line)",
    value=default_text,
    height=200,
    placeholder="Great product, fast shipping!\nBroke after one week. Very disappointed.",
)

# ─── Generate ─────────────────────────────────────────────────────────────────
if st.button("Generate Verdict", type="primary", use_container_width=True):
    reviews = [r.strip() for r in reviews_input.strip().splitlines() if r.strip()]

    if not reviews:
        st.warning("Please enter at least one review before generating a verdict.")
    else:
        with st.spinner("Analyzing reviews..."):
            try:
                result = call_api(reviews)
                render_verdict(result, reviews)
            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to backend. Make sure the API is running:\n\n"
                    "`uvicorn app.main:app --reload`"
                )
            except requests.exceptions.HTTPError as e:
                detail = ""
                try:
                    detail = e.response.json().get("detail", "")
                except Exception:
                    pass
                st.error(f"API error: {e} {detail}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
