from langgraph.store.memory import InMemoryStore

# Create store
store = InMemoryStore()

# Define namespace and key (like user/session ids)
namespace = "sessions"
session_id = "user_123"

# Store a session memory object (or just any dict/string for test)
session_data = {
    "summary": "User asked about diabetes",
    "buffer": [
        {"user": "What is diabetes?", "assistant": "It is a metabolic disorder."}
    ]
}

# Save it
store.put(namespace=namespace, key=session_id, value=session_data)

# Retrieve it
retrieved = store.get(namespace=namespace, key=session_id)
print("Retrieved session:", retrieved)

# List all sessions
all_sessions = store.list(namespace=namespace)
print("All session keys:", [item.key for item in all_sessions])
