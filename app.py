import streamlit as st
import random

# -----------------------------
# App config
# -----------------------------
st.set_page_config(page_title="WaterBuddy", page_icon="💧", layout="centered")

# -----------------------------
# Constants and helpers
# -----------------------------
AGE_GROUPS = {
    "Children (4–8)": 1200,   # ml
    "Teens (9–13)": 1700,
    "Adults (14–64)": 2200,   # midpoint of 2000–2500
    "Seniors (65+)": 1800
}

HYDRATION_TIPS = [
    "Sip water before meals.",
    "Keep a bottle on your desk.",
    "Set small goals every hour.",
    "Add a slice of lemon for taste.",
    "Drink a glass after you wake up.",
    "Use reminders during long tasks.",
    "Finish a cup after each break."
]

MASCOT_EMOJIS = {
    "start": "🫧",     # neutral bubbles
    "25": "🙂",
    "50": "😊",
    "75": "👋",       # wave
    "100": "👏",      # clap
    "over": "🎉"      # celebration
}


def init_state():
    """Initialize session state keys."""
    defaults = {
        "age_group": "Adults (14–64)",
        "standard_goal": AGE_GROUPS["Adults (14–64)"],
        "user_goal": AGE_GROUPS["Adults (14–64)"],
        "total": 0,
        "last_log": 0,
        "tips_enabled": True,
        "cups_to_ml": 250,  # converter assumption: 1 cup ~ 250 ml
        "theme_dark": False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def get_progress(total, goal):
    """Return progress percent and remaining ml, bounded."""
    goal = max(goal, 1)
    pct = max(0.0, min(100.0, (total / goal) * 100))
    remaining = max(0, goal - total)
    return round(pct, 1), remaining


def mascot_for_progress(pct, total, goal):
    """Choose mascot emoji based on progress milestones."""
    if total == 0:
        return MASCOT_EMOJIS["start"], "Let’s get your first sip in!"
    if pct < 25:
        return MASCOT_EMOJIS["25"], "Nice start — keep sipping."
    elif pct < 50:
        return MASCOT_EMOJIS["50"], "Great pace! You’re halfway to halfway."
    elif pct < 75:
        return MASCOT_EMOJIS["50"], "You’re past 50%. Keep going!"
    elif pct < 100:
        return MASCOT_EMOJIS["75"], "Strong progress — 75% reached!"
    elif pct == 100:
        return MASCOT_EMOJIS["100"], "Goal met — awesome consistency!"
    else:
        return MASCOT_EMOJIS["over"], "You’ve exceeded your goal — hydration hero!"


def log_water(amount_ml):
    """Add water intake to total."""
    st.session_state.total += max(0, int(amount_ml))
    st.session_state.last_log = int(amount_ml)


def reset_day():
    """Reset daily counters."""
    st.session_state.total = 0
    st.session_state.last_log = 0


def standard_vs_user_goal_text():
    return f"Standard: {st.session_state.standard_goal} ml | Your goal: {st.session_state.user_goal} ml"


# -----------------------------
# UI
# -----------------------------
def main():
    init_state()

    # Header
    st.title("WaterBuddy 💧")
    st.caption("Your friendly, age-aware hydration companion")

    # Sidebar: options and tips
    with st.sidebar:
        st.subheader("Daily tips")
        st.toggle("Show tips", value=st.session_state.tips_enabled, key="tips_enabled")
        if st.session_state.tips_enabled:
            st.info(random.choice(HYDRATION_TIPS))

        st.divider()
        st.subheader("Converters")
        st.number_input("Cup size (ml)", min_value=150, max_value=350, step=10, key="cups_to_ml")
        # Quick converter: cups -> ml
        cups = st.number_input("Cups to convert", min_value=0.0, step=0.5)
        st.write(f"= {int(cups * st.session_state.cups_to_ml)} ml")

    # Age group & goal
    st.header("Daily goal setup")
    cols = st.columns([2, 1, 1])
    with cols[0]:
        st.session_state.age_group = st.selectbox("Select age group", list(AGE_GROUPS.keys()), index=list(AGE_GROUPS.keys()).index(st.session_state.age_group))
        if AGE_GROUPS[st.session_state.age_group] != st.session_state.standard_goal:
            st.session_state.standard_goal = AGE_GROUPS[st.session_state.age_group]
            # If user hasn't customized, sync to standard
            if st.session_state.total == 0 or st.session_state.user_goal == st.session_state.standard_goal:
                st.session_state.user_goal = st.session_state.standard_goal

    with cols[1]:
        st.number_input("Suggested goal (ml)", value=st.session_state.standard_goal, disabled=True)
    with cols[2]:
        st.session_state.user_goal = st.number_input("Your goal (ml)", min_value=600, max_value=4000, step=50, value=st.session_state.user_goal)

    st.caption(standard_vs_user_goal_text())

    st.divider()

    # Progress and mascot
    st.header("Your hydration progress")
    pct, remaining = get_progress(st.session_state.total, st.session_state.user_goal)
    st.progress(pct / 100.0)
    emoji, message = mascot_for_progress(pct, st.session_state.total, st.session_state.user_goal)

    # Show bottle fill approximation (simple visual bar using text)
    bottle_cols = st.columns([1, 4])
    with bottle_cols[0]:
        st.markdown(f"### {emoji}")
        st.caption(message)
    with bottle_cols[1]:
        filled_blocks = int(pct // 10)
        empty_blocks = 10 - filled_blocks
        bar = "🟦" * filled_blocks + "⬜" * empty_blocks
        st.markdown(f"**Bottle fill:** {bar}")
        st.write(f"Total: {st.session_state.total} ml | Remaining: {remaining} ml | {pct}% of goal")

    st.divider()

    # Logging controls
    st.header("Log your water")
    log_cols = st.columns([1, 1, 1, 1])
    with log_cols[0]:
        if st.button("+250 ml"):
            log_water(250)
    with log_cols[1]:
        custom_ml = st.number_input("Custom amount (ml)", min_value=0, step=50)
        if st.button("Add custom ml"):
            log_water(custom_ml)
    with log_cols[2]:
        custom_cups = st.number_input("Custom cups", min_value=0.0, step=0.5)
        if st.button("Add cups"):
            log_water(int(custom_cups * st.session_state.cups_to_ml))
    with log_cols[3]:
        if st.button("New day 🔄"):
            reset_day()
            st.success("Daily counters reset.")

    # End-of-day summary (optional celebratory message)
    if pct >= 100:
        st.success("End-of-day summary: You hit your hydration goal today! 🎉")
        st.caption("Tip: Aim for slow, steady sipping tomorrow too.")

    st.divider()
    st.header("Why hydration matters")
    st.write(
        "- Supports energy and focus\n"
        "- Helps regulate body temperature\n"
        "- Aids digestion and skin health\n"
        "- Encourages healthy daily routines"
    )

    st.caption("Lightweight, private, and motivating — keep it simple and keep sipping.")


if __name__ == "__main__":
    main()
