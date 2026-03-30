import gradio as gr
import time
from crew import run_travel_crew, run_followup
from memory import ConversationMemory

memory = ConversationMemory()


# ───────────────────────────────
# Helpers
# ───────────────────────────────

def add_msg(history, role, content):
    history.append({"role": role, "content": content})
    return history


def trip_summary(dest, days, budget, style, ppl):
    return f"""
<div class="trip-card">
✈️ <b>{dest}</b><br>
{days} days · ${budget} · {style} · {ppl} travellers
</div>
"""


# ───────────────────────────────
# Streaming
# ───────────────────────────────

def stream_text(text):
    words = text.split(" ")
    output = ""
    for w in words:
        output += w + " "
        yield output
        time.sleep(0.01)


# ───────────────────────────────
# Core Logic
# ───────────────────────────────

def plan_trip(destination, duration, budget, style, people, history):
    if not destination.strip():
        return history, history

    history = history or []

    user_msg = trip_summary(destination, duration, budget, style, people)
    add_msg(history, "user", user_msg)

    add_msg(history, "assistant", "💜 Generating your perfect trip...")

    try:
        result = run_travel_crew({
            "destination": destination,
            "duration": int(duration),
            "budget": float(budget),
            "travel_style": style,
            "num_travelers": int(people),
            "context": memory.get_context(),
        })
    except Exception as e:
        result = f"❌ {e}"

    history[-1] = {"role": "assistant", "content": ""}

    for partial in stream_text(result):
        history[-1]["content"] = partial
        yield history, history

    memory.add(user_msg, result)


def followup(message, history):
    if not message.strip():
        return "", history

    history = history or []

    add_msg(history, "user", message)
    add_msg(history, "assistant", "✨ Updating your plan...")

    try:
        result = run_followup(message, memory.get_context())
    except Exception as e:
        result = f"❌ {e}"

    history[-1] = {"role": "assistant", "content": ""}

    for partial in stream_text(result):
        history[-1]["content"] = partial
        yield "", history

    memory.add(message, result)


def clear_all():
    memory.clear()
    return [], []


# ───────────────────────────────
# CSS (THIS IS THE MAGIC)
# ───────────────────────────────

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');

body {
    font-family: 'Poppins', sans-serif;
}

/* Chat bubbles */
.message.user {
    background: rgba(124, 58, 237, 0.2) !important;
    border-radius: 14px;
}

.message.bot {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 14px;
}

/* Trip summary card */
.trip-card {
    padding: 12px;
    border-radius: 12px;
    background: linear-gradient(135deg, #7c3aed33, #a78bfa33);
}

/* Section styling */
h2 {
    margin-top: 20px;
    padding: 10px;
    border-radius: 10px;
    background: rgba(124,58,237,0.15);
}

/* Buttons */
button.primary {
    background: linear-gradient(135deg, #7c3aed, #a78bfa) !important;
    border: none !important;
}

/* Inputs */
input, textarea, select {
    border-radius: 10px !important;
}

/* Sticky input bar */
textarea {
    background: rgba(255,255,255,0.05) !important;
}
"""


# ───────────────────────────────
# UI
# ───────────────────────────────

with gr.Blocks(
    title="AI Travel Planner",
    theme=gr.themes.Soft(primary_hue="violet"),
    css=CSS
) as demo:

    gr.Markdown("# 💜 AI Travel Planner")

    state = gr.State([])

    with gr.Row():

        # LEFT: CHAT
        with gr.Column(scale=2):

            chatbot = gr.Chatbot(height=600, show_label=False)

            with gr.Row():
                followup_box = gr.Textbox(
                    placeholder="✨ Refine your plan...",
                    scale=5,
                    container=False
                )
                send_btn = gr.Button("Send ✨", scale=1)

        # RIGHT: SETTINGS PANEL
        with gr.Column(scale=1):

            gr.Markdown("### ⚙️ Trip Settings")

            destination = gr.Textbox(label="📍 Destination")

            duration = gr.Slider(1, 21, value=7, step=1, label="📅 Days")

            budget = gr.Number(value=2000, label="💰 Budget")

            style = gr.Dropdown(
                ["🌄 Adventure", "🌴 Relaxation", "🏛 Cultural", "💎 Luxury", "🎒 Budget"],
                value="🏛 Cultural",
                label="🎨 Style"
            )

            people = gr.Slider(1, 10, value=2, step=1, label="👥 Travellers")

            plan_btn = gr.Button("🚀 Plan Trip", variant="primary")
            clear_btn = gr.Button("🧹 Clear")

    # Actions
    plan_btn.click(
        plan_trip,
        inputs=[destination, duration, budget, style, people, state],
        outputs=[chatbot, state],
    )

    send_btn.click(
        followup,
        inputs=[followup_box, state],
        outputs=[followup_box, chatbot],
    )

    followup_box.submit(
        followup,
        inputs=[followup_box, state],
        outputs=[followup_box, chatbot],
    )

    clear_btn.click(clear_all, outputs=[chatbot, state])


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)