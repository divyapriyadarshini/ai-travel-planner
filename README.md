# 💜 AI Travel Planner

An intelligent travel planning system built using a **multi-agent architecture (CrewAI)** with an interactive **Gradio interface**.

The system generates complete travel plans including destination insights, budget breakdowns, accommodation suggestions, and day-by-day itineraries, with support for follow-up refinements using contextual memory.

---

## 🚀 Features

* 🤖 Multi-agent system for task decomposition
* 📅 Structured day-by-day itinerary generation
* 💰 Budget estimation and breakdown
* 🏨 Accommodation recommendations
* 🧠 Context-aware memory for follow-up queries
* 🌐 Optional web search tool integration
* 💬 Streaming responses for real-time interaction
* 🎨 Clean and interactive UI (Gradio)

---

## 🧱 Tech Stack

* Python
* CrewAI
* OpenAI API
* Gradio
* python-dotenv

---

## 🧠 How It Works

The system uses multiple specialized agents, each responsible for a specific task:

* **Destination Researcher** → explores attractions, culture, logistics
* **Budget Planner** → creates a cost breakdown
* **Hotel Finder** → suggests accommodation options
* **Itinerary Generator** → builds a day-by-day plan

These agents are orchestrated sequentially using CrewAI, ensuring each step builds on previous outputs.

A lightweight memory module stores recent interactions, allowing users to refine plans with follow-up queries like:

> “Make it cheaper” or “Add more adventure activities”

---

## 📂 Project Structure

```id="9lgm2h"
app.py         # Gradio UI + streaming logic
crew.py        # Agents, tasks, orchestration
memory.py      # Conversation memory
requirements.txt
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash id="5x3u6k"
git clone https://github.com/divyapriyadarshini/ai-travel-planner
cd ai-travel-planner
```

### 2. Create virtual environment

```bash id="g9m3vs"
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash id="eq8m0f"
pip install -r requirements.txt
```

### 4. Add environment variables

Create a `.env` file:

```bash id="3k2z7v"
OPENAI_API_KEY=your_key_here
SERPER_API_KEY=your_key_here   # optional
```

---

## ▶️ Run the App

```bash id="5tdx2k"
python app.py
```

Open in browser:

```id="u1t9cn"
http://localhost:7860
```

---

## 🧪 Key Highlights (for Evaluation)

* Multi-agent system implemented using CrewAI → see `crew.py`
* Tool integration (optional Serper API) for external data
* Contextual memory for follow-up interactions → see `memory.py`
* Structured outputs enforced via task design
* Interactive UI with real-time streaming → see `app.py`

---

## 🚧 Future Improvements

* Integration with real-time travel APIs (flights, hotels)
* Export plans to PDF
* Save and load trip histories
* Personalization based on user preferences

---

## 👤 Author

Divya Priyadarshini
