# 🤖 ReAct Agent — Multi-Tool Setup

A minimal **ReAct (Reasoning + Acting)** agent built in Python that uses an LLM to solve problems step-by-step by reasoning and invoking tools in a loop.

## 📁 Project Structure

```
├── src/
│   └── react_agent.py      # Main agent code with all tools
├── screenshots/             # Output screenshots from Colab runs
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

## 🧰 Tools Used

| # | Tool | Description | Example Input |
|---|------|-------------|---------------|
| 1 | **🧮 Calculator** | Evaluates math expressions with support for `sqrt`, `sin`, `cos`, `log`, `pi`, `e`, etc. | `"sqrt(144) + 25 * 3"` |
| 2 | **💱 Currency Converter** | Converts between 15 currencies (USD, EUR, GBP, INR, JPY, AUD, CAD, CHF, CNY, SGD, AED, KRW, BRL, MXN, ZAR) | `"100 USD to INR"` |
| 3 | **📏 Unit Converter** | Converts length, weight, volume, speed, area, and temperature units | `"5 miles to km"` or `"100 f to c"` |

## ⚙️ Tech Stack

- **Language:** Python 3.10+
- **LLM Provider:** [Groq](https://console.groq.com) (free tier)
- **Model:** Llama 3.3 70B Versatile
- **Pattern:** ReAct (Thought → Action → Observation → ... → Final Answer)
- **Environment:** Google Colab

## 🚀 How to Run

### Option 1: Google Colab (Recommended)

1. Open [Google Colab](https://colab.research.google.com)
2. Create a new notebook
3. **Cell 1 — Install dependencies:**
   ```python
   !pip install -q groq
   ```
4. **Cell 2 — Paste the entire contents of `src/react_agent.py`** and run
5. **API Key Setup:**
   - Get a free API key at [console.groq.com/keys](https://console.groq.com/keys)
   - In Colab, click the 🔑 **Secrets** icon in the left sidebar
   - Add a new secret: Name = `GROQ_API_KEY`, Value = your key
   - Toggle "Notebook access" ON

### Option 2: Local

```bash
pip install -r requirements.txt
cd src
python react_agent.py
```

## 📝 Example Queries

```
"What is the square root of 144 plus 25 * 3?"
"Convert 500 USD to INR"
"How many kilometers is 26.2 miles?"
"Convert 100 Fahrenheit to Celsius"
"If I have 250 EUR, how much is that in Japanese Yen?"
```

## 🔄 How the ReAct Pattern Works

```
User Query
    ↓
┌─────────────────────────┐
│ Thought: LLM reasons    │
│ Action:  calls a tool   │──→ Tool executes
│ Observation: result     │←── Result returned
└─────────┬───────────────┘
          ↓ (repeat if needed)
    Final Answer
```

1. The LLM receives the user query and available tools
2. It generates a **Thought** (reasoning about what to do)
3. It picks an **Action** (tool call with input)
4. The agent executes the tool and returns the **Observation**
5. The LLM continues reasoning until it produces a **Final Answer**

## 🔍 Observations

- **ReAct pattern** is effective for structured problem-solving — the LLM "thinks out loud" before acting, reducing errors.
- **Groq + Llama 3.3 70B** provides fast inference on the free tier (~30 RPM), making it a great alternative to rate-limited APIs.
- **Multi-tool setup** demonstrates how the agent dynamically selects the right tool based on the query — no hardcoded routing needed.
- **Temperature = 0** ensures deterministic, consistent outputs for tool-calling tasks.
- **Retry with backoff** handles transient rate limits gracefully without crashing.

## 📸 Screenshots

Output screenshots from Colab runs are stored in the `/screenshots` directory.

## 📄 License

This project is for educational/demonstration purposes.
