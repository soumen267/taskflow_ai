import json
import ollama
import datetime
from django.utils import timezone
from google import genai
from google.genai import types
from django.conf import settings

# 🎛️ GLOBAL AI ENGINE CONFIGURATION
AI_ENGINE_SELECTION = 1  # 1 = Ollama (Local), 2 = Gemini (Cloud)

def get_gemini_client():
    """Initializes the official Google GenAI client securely using your environment configurations."""
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    return genai.Client(api_key=api_key)

def call_ai_engine(system_instruction, prompt_text, temperature=0.0, require_json=False):
    """
    GLOBAL HELPER FUNCTION: Channels prompts to either Ollama or Gemini 
    based on the AI_ENGINE_SELECTION switch, handles errors, and cleans output text.
    """
    engine_name = "OLLAMA LOCAL" if AI_ENGINE_SELECTION == 1 else "GEMINI CLOUD"
    
    try:
        if AI_ENGINE_SELECTION == 1:
            # 1️⃣ OLLAMA SPECIFIC CORES
            response = ollama.generate(
                model='qwen2.5-coder:3b',
                system=system_instruction,
                prompt=prompt_text,
                options={"temperature": temperature}
            )
            raw_output = response['response']
        else:
            # 2️⃣ GEMINI SPECIFIC CORES
            client = get_gemini_client()
            
            # Setup configuration arguments dynamically
            config_args = {
                "system_instruction": system_instruction,
                "temperature": temperature
            }
            if require_json:
                config_args["response_mime_type"] = "application/json"
                
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_text,
                config=types.GenerateContentConfig(**config_args),
            )
            raw_output = response.text

        # Standard Clean-up Operations for both engines
        clean_output = raw_output.strip().replace("```json", "").replace("```html", "").replace("```", "")
        return clean_output

    except Exception as e:
        print(f"❌ [GLOBAL AI ENGINE ERROR] Platform: {engine_name} | Exception: {e}")
        return None

# =====================================================================
# 🛠️ YOUR REORGANIZED COMPONENT FUNCTIONS (NOW MUCH SMALLER & CLEANER)
# =====================================================================

def parse_task_with_ollama(prompt_text):
    """Parses unstructured conversational sentences into structured JSON data rows."""
    today_str = timezone.now().date().strftime("%Y-%m-%d")

    system_instruction = (
        "You are a strict backend data parser for a task management system. "
        "Your job is to parse unstructured sentences into a structured JSON object.\n\n"
        f"CRITICAL CONTEXT: Today's date is strictly {today_str}. "
        "Use this reference date to calculate any relative time expressions mentioned (e.g., 'tomorrow').\n\n"
        "The JSON object MUST contain exactly these keys: 'title', 'priority', 'assigned_to', 'client', 'due_date'.\n"
        "Do not explain anything. Output ONLY the raw JSON string."
    )

    # Use the global helper
    raw_json_str = call_ai_engine(
        system_instruction=system_instruction,
        prompt_text=f"Parse this task sentence: '{prompt_text}'",
        temperature=0.0,
        require_json=True
    )

    if not raw_json_str:
        return None

    try:
        return json.loads(raw_json_str)
    except Exception as e:
        print(f"❌ JSON Parsing Error: {e}")
        return None

    
def generate_workspace_brief(user_name, tasks_list, is_admin=False):
    """Generates an HTML workspace focus brief optimized based on the user's workflow role."""
    if not tasks_list:
        return "<p class='text-muted mb-0'>🎉 <strong>All clean!</strong> You have no pending tasks.</p>"
    
    current_hour = datetime.datetime.now().hour
    greeting = "Good morning" if current_hour < 12 else "Good afternoon" if current_hour < 17 else "Good evening"

    # Format the data rows
    formatted_tasks = []
    for t in tasks_list:
        client_name = t.client.name if t.client else "Internal"
        due = t.due_date.strftime('%Y-%m-%d') if t.due_date else "No deadline"
        assignee = t.assigned_to.username if t.assigned_to else "Unassigned"
        if is_admin:
            formatted_tasks.append(f"- [{t.priority.upper()}] '{t.title}' for {client_name} (Assigned to: {assignee}, Due: {due})")
        else:
            formatted_tasks.append(f"- [{t.priority.upper()}] '{t.title}' for {client_name} (Due: {due})")
            
    tasks_context = "\n".join(formatted_tasks)

    role_instruction = (
        "You are an elite Operations Director AI giving the Administrator high-level operational oversight summaries."
        if is_admin else
        "You are an elite productivity executive assistant giving the user a highly motivating personal workspace focus plan."
    )

    system_instruction = (
        f"{role_instruction}\n\n"
        "FORMATTING RULES:\n"
        "1. Strict HTML Only: Do NOT use markdown. Write pure HTML tags directly.\n"
        f"2. Start your response directly with: '<p>{greeting}, {user_name}!</p>'\n"
        "3. Structure your response using exactly two distinct <p> blocks or an <ul> list.\n"
        "4. Keep your output highly precise, professional, and under 120 words.\n"
    )

    # Use the global helper
    brief_html = call_ai_engine(
        system_instruction=system_instruction,
        prompt_text=f"Generate a workspace focus brief based on these active data rows:\n{tasks_context}",
        temperature=0.2,
        require_json=False
    )

    if not brief_html:
        return "<p class='text-muted'>My circuits are temporarily offline. Have a productive day!</p>"

    return brief_html