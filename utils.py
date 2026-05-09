import json
from datetime import datetime

def safe_json_load(data):
    if not data or data == "" or data is None:
        return []
    try:
        return json.loads(data)
    except:
        return []

def add_log(ticket, message):
    logs = safe_json_load(ticket.logs)
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    logs.append(f"{now} - {message}")
    ticket.logs = json.dumps(logs)