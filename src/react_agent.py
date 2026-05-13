# =============================================================================
# 🤖 Minimal ReAct Agent — Google Colab Ready
# =============================================================================
# Pattern: Thought → Action → Observation → ... → Final Answer
# LLM: Groq (free tier — Llama 3.3 70B)
# =============================================================================

# --- Cell 1: Install dependency ---
!pip install -q groq

# --- Cell 2: Full ReAct Agent ---

import re
import time
import math
import os
from groq import Groq

# ── Configure API Key ────────────────────────────────────────────────────────
# Priority: 1. Colab Secrets | 2. Environment Variables | 3. Manual Input
API_KEY = None

# Try Colab Secrets (only if running in Colab)
if os.path.exists('/content'):
    try:
        import importlib
        userdata = importlib.import_module('google.colab.userdata')
        API_KEY = userdata.get("GROQ_API_KEY")
    except (ImportError, ModuleNotFoundError):
        pass

# Try Environment Variable
if not API_KEY:
    API_KEY = os.environ.get("GROQ_API_KEY")

# Fallback to manual input
if not API_KEY:
    import getpass
    print("🔑 Groq API key not found in Colab Secrets or Environment Variables.")
    API_KEY = getpass.getpass("Enter your Groq API key: ")

if not API_KEY:
    raise ValueError("API Key is required to run the agent.")

client = Groq(api_key=API_KEY)


# ══════════════════════════════════════════════════════════════════════════════
#                              TOOLS
# ══════════════════════════════════════════════════════════════════════════════

# ── Tool 1: Calculator ──────────────────────────────────────────────────────

def calculator(expression: str) -> str:
    """Evaluate a math expression and return the result.
    Supports basic arithmetic and math functions (sqrt, sin, cos, log, pi, etc.)."""
    safe_globals = {"__builtins__": {}}
    safe_locals = {
        "math": math,
        "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
        "tan": math.tan, "log": math.log, "log10": math.log10,
        "pi": math.pi, "e": math.e, "pow": pow, "abs": abs,
        "round": round, "ceil": math.ceil, "floor": math.floor,
    }
    try:
        result = eval(expression, safe_globals, safe_locals)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


# ── Tool 2: Currency Converter ──────────────────────────────────────────────

# Exchange rates relative to 1 USD (approximate)
EXCHANGE_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "INR": 83.50,
    "JPY": 154.80,
    "AUD": 1.53,
    "CAD": 1.36,
    "CHF": 0.88,
    "CNY": 7.24,
    "SGD": 1.34,
    "AED": 3.67,
    "KRW": 1330.0,
    "BRL": 4.97,
    "MXN": 17.15,
    "ZAR": 18.60,
}

def currency_converter(query: str) -> str:
    """Convert an amount from one currency to another.
    Input format: '<amount> <FROM_CURRENCY> to <TO_CURRENCY>'
    Example: '100 USD to INR'
    """
    try:
        # Parse: "100 USD to INR" or "100 usd to inr"
        pattern = r"([\d.]+)\s*([A-Za-z]{3})\s+to\s+([A-Za-z]{3})"
        match = re.match(pattern, query.strip())
        if not match:
            return (
                "Error: Invalid format. Use '<amount> <FROM> to <TO>'. "
                "Example: '100 USD to INR'"
            )

        amount = float(match.group(1))
        from_cur = match.group(2).upper()
        to_cur = match.group(3).upper()

        if from_cur not in EXCHANGE_RATES:
            return f"Error: Unsupported currency '{from_cur}'. Supported: {', '.join(sorted(EXCHANGE_RATES))}"
        if to_cur not in EXCHANGE_RATES:
            return f"Error: Unsupported currency '{to_cur}'. Supported: {', '.join(sorted(EXCHANGE_RATES))}"

        # Convert: from_cur → USD → to_cur
        usd_amount = amount / EXCHANGE_RATES[from_cur]
        converted = usd_amount * EXCHANGE_RATES[to_cur]

        return f"{amount} {from_cur} = {converted:,.2f} {to_cur}"

    except Exception as e:
        return f"Error: {e}"


# ── Tool 3: Unit Converter ──────────────────────────────────────────────────

# Conversion factors to a base unit within each category
UNIT_CONVERSIONS = {
    # Length → base: meter
    "km": ("length", 1000),
    "m": ("length", 1),
    "cm": ("length", 0.01),
    "mm": ("length", 0.001),
    "mile": ("length", 1609.344),
    "miles": ("length", 1609.344),
    "yard": ("length", 0.9144),
    "yards": ("length", 0.9144),
    "foot": ("length", 0.3048),
    "feet": ("length", 0.3048),
    "ft": ("length", 0.3048),
    "inch": ("length", 0.0254),
    "inches": ("length", 0.0254),
    "in": ("length", 0.0254),

    # Weight → base: kilogram
    "kg": ("weight", 1),
    "g": ("weight", 0.001),
    "mg": ("weight", 0.000001),
    "lb": ("weight", 0.453592),
    "lbs": ("weight", 0.453592),
    "oz": ("weight", 0.0283495),
    "ton": ("weight", 1000),
    "tons": ("weight", 1000),

    # Volume → base: liter
    "l": ("volume", 1),
    "liter": ("volume", 1),
    "liters": ("volume", 1),
    "ml": ("volume", 0.001),
    "gallon": ("volume", 3.78541),
    "gallons": ("volume", 3.78541),
    "gal": ("volume", 3.78541),
    "cup": ("volume", 0.236588),
    "cups": ("volume", 0.236588),
    "pint": ("volume", 0.473176),
    "pints": ("volume", 0.473176),

    # Speed → base: m/s
    "m/s": ("speed", 1),
    "km/h": ("speed", 0.277778),
    "kmph": ("speed", 0.277778),
    "mph": ("speed", 0.44704),
    "knot": ("speed", 0.514444),
    "knots": ("speed", 0.514444),

    # Area → base: sq meter
    "sqm": ("area", 1),
    "sqkm": ("area", 1_000_000),
    "sqft": ("area", 0.092903),
    "sqmi": ("area", 2_589_988),
    "acre": ("area", 4046.86),
    "acres": ("area", 4046.86),
    "hectare": ("area", 10_000),
    "hectares": ("area", 10_000),

    # Temperature (handled specially)
    "c": ("temperature", None),
    "celsius": ("temperature", None),
    "f": ("temperature", None),
    "fahrenheit": ("temperature", None),
    "k": ("temperature", None),
    "kelvin": ("temperature", None),
}

def _convert_temperature(value: float, from_u: str, to_u: str) -> float:
    """Convert temperature between C, F, and K."""
    # Normalize names
    from_u = {"celsius": "c", "fahrenheit": "f", "kelvin": "k"}.get(from_u, from_u)
    to_u = {"celsius": "c", "fahrenheit": "f", "kelvin": "k"}.get(to_u, to_u)

    # To Celsius first
    if from_u == "c":
        c = value
    elif from_u == "f":
        c = (value - 32) * 5 / 9
    elif from_u == "k":
        c = value - 273.15
    else:
        raise ValueError(f"Unknown temperature unit: {from_u}")

    # From Celsius to target
    if to_u == "c":
        return c
    elif to_u == "f":
        return c * 9 / 5 + 32
    elif to_u == "k":
        return c + 273.15
    else:
        raise ValueError(f"Unknown temperature unit: {to_u}")

def unit_converter(query: str) -> str:
    """Convert a value from one unit to another.
    Input format: '<value> <from_unit> to <to_unit>'
    Example: '5 miles to km' or '100 f to c'
    """
    try:
        pattern = r"([\d.]+)\s*([A-Za-z/]+)\s+to\s+([A-Za-z/]+)"
        match = re.match(pattern, query.strip())
        if not match:
            return (
                "Error: Invalid format. Use '<value> <from_unit> to <to_unit>'. "
                "Example: '5 miles to km'"
            )

        value = float(match.group(1))
        from_unit = match.group(2).lower()
        to_unit = match.group(3).lower()

        if from_unit not in UNIT_CONVERSIONS:
            return f"Error: Unknown unit '{from_unit}'"
        if to_unit not in UNIT_CONVERSIONS:
            return f"Error: Unknown unit '{to_unit}'"

        from_cat, from_factor = UNIT_CONVERSIONS[from_unit]
        to_cat, to_factor = UNIT_CONVERSIONS[to_unit]

        if from_cat != to_cat:
            return f"Error: Cannot convert between '{from_unit}' ({from_cat}) and '{to_unit}' ({to_cat})"

        # Special case: temperature
        if from_cat == "temperature":
            result = _convert_temperature(value, from_unit, to_unit)
            return f"{value} {from_unit.upper()} = {result:.2f} {to_unit.upper()}"

        # Standard conversion: value → base → target
        base_value = value * from_factor
        result = base_value / to_factor

        return f"{value} {from_unit} = {result:,.4f} {to_unit}"

    except Exception as e:
        return f"Error: {e}"




# ══════════════════════════════════════════════════════════════════════════════
#                          TOOL REGISTRY & PROMPT
# ══════════════════════════════════════════════════════════════════════════════

TOOLS = {
    "calculator": calculator,
    "currency_converter": currency_converter,
    "unit_converter": unit_converter,
}

TOOL_DESCRIPTIONS = """
Available tools:
1. calculator(expression)        — Evaluates a math expression. Supports +, -, *, /, **, sqrt(), sin(), cos(), log(), pi, e.
2. currency_converter(query)     — Converts between currencies. Input: "<amount> <FROM> to <TO>". Example: "100 USD to INR".
3. unit_converter(query)         — Converts between units (length, weight, temp, etc.). Input: "<value> <from_unit> to <to_unit>".
""".strip()

# ── System Prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = f"""You are a ReAct agent. You solve problems step-by-step using Thought/Action/Observation loops.

{TOOL_DESCRIPTIONS}

Respond using EXACTLY this format (no deviation):

Thought: <your reasoning about what to do next>
Action: <tool_name>(<input>)

After each Observation you receive, continue with another Thought/Action or finish with:

Thought: <final reasoning>
Final Answer: <your answer to the user>

Rules:
- Always start with a Thought.
- Use ONLY the tools listed above.
- Call ONE tool per step.
- Once you know the answer, output "Final Answer:" and stop.
"""


# ══════════════════════════════════════════════════════════════════════════════
#                           ReAct AGENT LOOP
# ══════════════════════════════════════════════════════════════════════════════

def run_react_agent(user_query: str, max_steps: int = 8, verbose: bool = True) -> str:
    """Run the ReAct agent on a user query."""

    if verbose:
        print("=" * 60)
        print(f"🧑 User Query: {user_query}")
        print("=" * 60)

    # Build conversation history (OpenAI chat format)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    for step in range(1, max_steps + 1):
        if verbose:
            print(f"\n--- Step {step} ---")

        # Get LLM response (with retry for rate limits)
        llm_text = None
        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0,
                    max_tokens=1024,
                )
                llm_text = response.choices[0].message.content.strip()
                break
            except Exception as e:
                err_msg = str(e).lower()
                if "rate" in err_msg or "429" in err_msg or "limit" in err_msg:
                    wait_time = 2 ** (attempt + 1)  # 2, 4, 8 seconds
                    if verbose:
                        print(f"⏳ Rate limited. Retrying in {wait_time}s... (attempt {attempt + 1}/3)")
                    time.sleep(wait_time)
                else:
                    raise
        if llm_text is None:
            return "Error: API rate limit exceeded after 3 retries. Please wait and try again."

        if verbose:
            print(llm_text)

        # Check for Final Answer
        if "Final Answer:" in llm_text:
            final = llm_text.split("Final Answer:")[-1].strip()
            if verbose:
                print("\n" + "=" * 60)
                print(f"✅ Final Answer: {final}")
                print("=" * 60)
            return final

        # Parse Action (using greedy match to handle nested parentheses like calculator("sqrt(144)"))
        action_match = re.search(r"Action:\s*(\w+)\((.+)\)", llm_text)
        if not action_match:
            if verbose:
                print("⚠️  No action found, asking LLM to continue...")
            messages.append({"role": "assistant", "content": llm_text})
            messages.append({
                "role": "user",
                "content": "Please continue with a Thought and Action using the correct format.",
            })
            continue

        tool_name = action_match.group(1)
        tool_input = action_match.group(2).strip().strip("\"'")

        # Execute tool
        if tool_name in TOOLS:
            observation = TOOLS[tool_name](tool_input)
        else:
            observation = f"Error: Unknown tool '{tool_name}'"

        if verbose:
            print(f"\n🔧 Tool: {tool_name}({tool_input})")
            print(f"📋 Observation: {observation}")

        # Append to conversation
        messages.append({"role": "assistant", "content": llm_text})
        messages.append({
            "role": "user",
            "content": f"Observation: {observation}",
        })

    return "Agent reached max steps without a final answer."


# ══════════════════════════════════════════════════════════════════════════════
#                              RUN IT!
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🤖 Welcome to the ReAct Agent! (Type 'exit' or 'quit' to stop)")
    while True:
        try:
            query = input("\n💬 You: ").strip()
            if query.lower() in ["exit", "quit"]:
                print("Goodbye! 👋")
                break
            if not query:
                continue
            
            run_react_agent(query)
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")

