from conversation.manager import start_conversation, get_response, reset_conversation , list_active_sessions

session = start_conversation("user_123")
resp = get_response(session, "What is diabetic retinopathy?")
print("Bot:", resp)

print("\n\n\nSessions now: " , list_active_sessions)

resp2 = get_response(session, "What treatments are available?")
print("Bot:", resp2)

#reset_conversation(session)
