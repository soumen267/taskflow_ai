import json
import ollama
import datetime
from django.utils import timezone

def parse_task_with_ollama(prompt_text):
    """
    Sends unstructured user input to a local Ollama model 
    and extracts a clean, structured JSON object for Django.
    """
    today_str = timezone.now().date().strftime("%Y-%m-%d")

    system_instruction = (
        "You are a strict backend data parser for a task management system. "
        "Your job is to parse unstructured sentences into a structured JSON object.\n\n"
        f"CRITICAL CONTEXT: Today's date is strictly {today_str}. "
        "Use this reference date to calculate any relative time expressions mentioned (e.g., 'tomorrow', 'next monday', 'by friday').\n\n"
        "The JSON object MUST contain exactly these keys with no extra text or markdown wrappers:\n"
        "{\n"
        '  "title": "string containing the core task action",\n'
        '  "priority": "low", "medium", or "high" (default to "medium" if unspecified),\n'
        '  "assigned_to": "username string if mentioned, otherwise null",\n'
        '  "client": "client name string if mentioned, otherwise null",\n'
        '  "due_date": "Calculate and output ONLY as an absolute date string in YYYY-MM-DD format based on the reference date. If no date or time is mentioned, output null."\n'
        "}\n"
        "Do not explain anything. Output ONLY the raw JSON string."
    )
    print("\n" + "="*60)
    print(f"🤖 [AI START] Processing command: '{prompt_text}'")
    print("="*60)
    try:
        response = ollama.generate(
            model='qwen2.5-coder:3b',
            system=system_instruction,
            prompt=f"Parse this task sentence: '{prompt_text}'",
            options={"temperature": 0.0} # Zero temperature locks down predictable accuracy
        )
        raw_output = response['response']
        print("📥 [OLLAMA RAW OUTPUT]:")
        print(raw_output)
        print("-"*60)
        # Clean potential markdown string wrappers from the LLM output
        clean_json_str = response['response'].strip().replace("```json", "").replace("```", "")
        parsed_data = json.loads(clean_json_str)
        print(f"✅ [AI SUCCESS] Structured Data: {parsed_data}")
        print("="*60 + "\n")
        return parsed_data
    except Exception as e:
        print(f"AI Parsing Error: {e}")
        print(f"❌ [AI ERROR] Exception encountered: {e}")
        print("="*60 + "\n")
        return None
    
def generate_workspace_brief(user_name, tasks_list, is_admin=False):
    """
    Takes a structured list of pending tasks for a user and runs it through 
    Ollama to generate a highly focused, motivating, and clear HTML-formatted morning briefing.
    """
    if not tasks_list:
        return (
            "<p class='text-muted mb-0'>"
            "🎉 <strong>All clean!</strong> You have no pending tasks on your plate right now."
            "</p>"
        )
    
    # 1. 🕒 DYNAMIC TIME-OF-DAY GREETING
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning"
    elif current_hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    # Format the task data cleanly for the LLM context
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

    if is_admin:
        role_instruction = (
            "You are an elite Operations Director AI. Your job is to look at ALL pending company tasks "
            "and give the Administrator a high-level operational oversight summary.\n"
            "Highlight which team members have high-priority bottlenecks and flag any overdue targets."
        )
    else:
        role_instruction = (
            "You are an elite productivity executive assistant. Your job is to look at a user's personal "
            "pending tasks and give them a highly motivating personal workspace focus plan."
        )

    system_instruction = (
        "You are an elite productivity executive assistant. Your job is to read a user's pending "
        "tasks list and generate a brief, highly motivating, structured workspace summary.\n\n"
        "FORMATTING RULES:\n"
        "1. Strict HTML Only: Do NOT use markdown. Write pure HTML tags directly.\n"
        f"2. Start your response directly with: '<p>{greeting}, {user_name}!</p>'\n"
        "3. Structure your response using exactly two distinct <p> blocks or an <ul> list:\n"
        "   - Paragraph 1: High-priority tasks and urgent bottlenecks.\n"
        "   - Paragraph 2: Overdue alerts (like Task 2) and general recommendations.\n"
        "4. Keep your output highly precise, professional, and under 120 words.\n"
        "5. Do not wrap code inside markdown blocks like ```html.\n"
    )

    prompt = (
        f"Generate a workspace focus brief based on these active data rows:\n{tasks_context}"
    )

    try:
        response = ollama.generate(
            model='qwen2.5-coder:3b',  # Your fastest and most efficient local model
            system=system_instruction,
            prompt=prompt,
            options={"temperature": 0.2}  # Balanced between structure and creativity
        )
        return response['response'].strip().replace("```html", "").replace("```", "")
    except Exception as e:
        print(f"❌ [COPILOT ERROR]: {e}")
        return "<p class='text-muted'>My circuits are temporarily offline. Have a productive day!</p>"