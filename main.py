from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import time, os

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# --- In-memory storage ---
chats = []
logs = []
chat_counter = 1

# --- Homepage -> serve index.html ---
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# --- Get all chats ---
@app.route("/msgssender/chats", methods=["GET"])
def get_chats():
    return jsonify(chats)

# --- Create new chat ---
@app.route("/msgssender/create", methods=["POST"])
def create_chat():
    global chat_counter
    data = request.json or {}
    chat = {
        "id": chat_counter,
        "name": data.get("name", f"Chat {chat_counter}"),
        "timer": 30,
        "short": "",
        "enabled": False,
        "profileIds": [],
        "messages": [],
        "tokens": []
    }
    chats.append(chat)
    chat_counter += 1
    add_log("success", f"Created chat {chat['name']}")
    return jsonify({"success": True, "chat": chat})

# --- Update chat ---
@app.route("/msgssender/update/<int:chat_id>", methods=["POST"])
def update_chat(chat_id):
    data = request.json or {}
    for chat in chats:
        if chat["id"] == chat_id:
            if "name" in data:
                chat["name"] = data["name"]
            if "timer" in data:
                try:
                    chat["timer"] = int(data["timer"])
                except:
                    pass
            if "short" in data:
                chat["short"] = data["short"]
            if "enabled" in data:
                chat["enabled"] = bool(data["enabled"])
            if "profileIds" in data:
                chat["profileIds"] = data["profileIds"]
            if "messages" in data:
                chat["messages"] = data["messages"]
            if "tokens" in data:
                chat["tokens"] = data["tokens"]
            add_log("success", f"Updated chat {chat['name']}")
            return jsonify({"success": True, "chat": chat})
    return jsonify({"error": "Chat not found"}), 404

# --- Delete chat ---
@app.route("/msgssender/delete/<int:chat_id>", methods=["DELETE"])
def delete_chat(chat_id):
    global chats
    chats = [c for c in chats if c["id"] != chat_id]
    add_log("success", f"Deleted chat {chat_id}")
    return jsonify({"success": True})

# --- Test chat ---
@app.route("/msgssender/test/<int:chat_id>", methods=["POST"])
def test_chat(chat_id):
    target = next((c for c in chats if c["id"] == chat_id), None)
    if not target:
        return jsonify({"error": "Chat not found"}), 404
    add_log("success", f"Test simulated for chat {chat_id}")
    return jsonify({"success": True})

# --- Start chat ---
@app.route("/msgssender/start/<int:chat_id>", methods=["POST"])
def start_chat(chat_id):
    target = next((c for c in chats if c["id"] == chat_id), None)
    if not target:
        return jsonify({"error": "Chat not found"}), 404
    target["enabled"] = True
    add_log("success", f"Started chat {chat_id}")
    return jsonify({"success": True})

# --- Stop chat ---
@app.route("/msgssender/stop/<int:chat_id>", methods=["POST"])
def stop_chat(chat_id):
    target = next((c for c in chats if c["id"] == chat_id), None)
    if not target:
        return jsonify({"error": "Chat not found"}), 404
    target["enabled"] = False
    add_log("success", f"Stopped chat {chat_id}")
    return jsonify({"success": True})

# --- Logs ---
@app.route("/msgssender/logs", methods=["GET"])
def get_logs():
    return jsonify(logs)

# --- Helper ---
def add_log(status, message):
    logs.append({
        "status": status,
        "message": message,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    if len(logs) > 200:
        del logs[0: len(logs)-200]

# --- Health check ---
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
