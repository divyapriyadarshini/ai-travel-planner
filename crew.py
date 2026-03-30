import os
from dotenv import load_dotenv

load_dotenv()

from crewai import Agent, Task, Crew, Process

# ── Optional web search ───────────────────────────────────────
tools = []
if os.getenv("SERPER_API_KEY"):
    try:
        from crewai_tools import SerperDevTool
        tools = [SerperDevTool()]
        print("✅ SerperDevTool loaded — agents will use live web search.")
    except ImportError:
        print("⚠️ crewai-tools not installed. Running without live search.")
else:
    print("ℹ️ No SERPER_API_KEY set. Agents will use GPT knowledge only.")

# ── LLM FIX (IMPORTANT) ───────────────────────────────────────
# Instead of ChatOpenAI → use model string
llm = "gpt-4o-mini"


# ── Agents (UNCHANGED — KEEPING YOUR DETAIL) ──────────────────
def make_agents():
    destination_researcher = Agent(
        role="Destination Researcher",
        goal=(
            "Research the travel destination thoroughly — top attractions, "
            "best seasons to visit, local culture, visa requirements, and safety tips."
        ),
        backstory=(
            "You are a seasoned travel journalist who has visited 80+ countries. "
            "You provide vivid, accurate, and practical destination overviews."
        ),
        tools=tools,
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    budget_planner = Agent(
        role="Budget Planner",
        goal=(
            "Create a realistic and detailed budget breakdown for the trip, "
            "covering flights, accommodation, food, activities, and contingency."
        ),
        backstory=(
            "You are a financial travel expert who specialises in creating "
            "value-optimised travel budgets for every type of traveller."
        ),
        tools=tools,
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    hotel_finder = Agent(
        role="Hotel Finder",
        goal=(
            "Find the best accommodation options that match the traveller's "
            "budget and style, with names, price ranges, locations, and highlights."
        ),
        backstory=(
            "You are a hospitality consultant with deep knowledge of accommodation "
            "across all budget levels — from hostels to luxury resorts."
        ),
        tools=tools,
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    itinerary_generator = Agent(
        role="Itinerary Generator",
        goal=(
            "Combine all research into a beautifully structured, day-by-day "
            "travel itinerary that is logical, exciting, and time-efficient."
        ),
        backstory=(
            "You are a master trip planner who creates itineraries that balance "
            "must-see landmarks, hidden gems, rest time, and local experiences."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    return destination_researcher, budget_planner, hotel_finder, itinerary_generator


# ── Tasks (UNCHANGED — YOUR STRONG PART) ──────────────────────
def make_tasks(agents, inputs: dict):
    destination_researcher, budget_planner, hotel_finder, itinerary_generator = agents
    dest      = inputs["destination"]
    days      = inputs["duration"]
    budget    = inputs["budget"]
    style     = inputs["travel_style"]
    travelers = inputs["num_travelers"]
    context   = inputs.get("context", "No prior context.")

    research_task = Task(
        description=(
            f"""Research {dest} for {travelers} travellers on a {style} trip for {days} days.

Include:
- Top attractions
- Best areas to stay
- Local cuisine
- Transport options
- Safety tips
- Visa info
- Cultural etiquette

Use prior context:
{context}
"""
        ),
        expected_output=(
            """Return STRICTLY in Markdown:

## 📍 Destination Guide
### 🌍 Overview
### 🏝 Top Attractions
### 🍜 Local Food
### 🚆 Transport
### 🛡 Safety
### 📄 Visa & Entry
### 🤝 Cultural Tips
"""
        ),
        agent=destination_researcher,
    )

    budget_task = Task(
        description=(
            f"""Create a detailed budget for {dest} for {travelers} travellers for {days} days.
Total budget: ${budget}. Style: {style}.

Include:
- Flights
- Accommodation
- Food
- Activities
- Local transport
- 10% contingency
"""
        ),
        expected_output=(
            """Return STRICTLY in Markdown:

## 💰 Budget Breakdown
| Category | Cost (USD) |
|----------|-----------|
| Flights  |           |
| Hotels   |           |
| Food     |           |
| Activities |        |
| Transport |        |
| Misc     |        |

### 💡 Money Saving Tips
- Tip 1
- Tip 2
- Tip 3
"""
        ),
        agent=budget_planner,
        context=[research_task],
    )

    hotel_task = Task(
        description=(
            f"""Find 4–6 accommodation options in {dest} for {travelers} travellers.

Constraints:
- Match {style} style
- Stay within ~30% of ${budget}
- Provide variety (budget → luxury)
"""
        ),
        expected_output=(
            """Return STRICTLY in Markdown:

## 🏨 Hotels

### 🏨 Hotel 1
- Area:
- Price per night:
- Highlights:
- Pros:
- Cons:

### 🏨 Hotel 2
...
"""
        ),
        agent=hotel_finder,
        context=[research_task, budget_task],
    )

    itinerary_task = Task(
        description=(
            f"""Create a detailed {days}-day itinerary for {dest}.

Requirements:
- Morning / Afternoon / Evening per day
- Include activities + food
- Include estimated cost per day
- Add 1 insider tip daily
"""
        ),
        expected_output=(
            f"""Return STRICTLY in Markdown:

## 📅 Itinerary

### Day 1
**Morning:**
- Activity

**Afternoon:**
- Activity

**Evening:**
- Activity

💡 Tip:
💰 Estimated Cost:

### Day 2
...
"""
        ),
        agent=itinerary_generator,
        context=[research_task, budget_task, hotel_task],
    )

    return [research_task, budget_task, hotel_task, itinerary_task]


# ── Run Crew ──────────────────────────────────────────────────
def run_travel_crew(inputs: dict) -> str:
    agents = make_agents()
    tasks  = make_tasks(agents, inputs)

    crew = Crew(
        agents=list(agents),
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    return str(crew.kickoff())


# ── Follow-up Agent ───────────────────────────────────────────
def run_followup(message: str, context: str) -> str:
    advisor = Agent(
        role="Travel Advisor",
        goal="Refine and answer follow-up questions about an already-planned trip.",
        backstory=(
            "You are a knowledgeable travel advisor who helps travellers adjust "
            "and improve their existing plans based on new requirements."
        ),
        tools=tools,
        llm=llm,
        verbose=True,
    )

    task = Task(
        description=(
            f"Previous travel plan context:\n{context}\n\n"
            f"Follow-up request: {message}\n\n"
            "Be specific, practical, and concise."
        ),
        expected_output="A helpful, specific answer or revised plan section.",
        agent=advisor,
    )

    crew = Crew(agents=[advisor], tasks=[task], process=Process.sequential)

    return str(crew.kickoff())