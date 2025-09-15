from langchain.memory import ConversationBufferMemory , ConversationSummaryMemory
from langchain.chat_models import ChatOpenAI
import json
import os
from collections import deque
from openai import OpenAI

llm = ChatOpenAI(model = "gpt-3.5-turbo-0125" , temperature = 0)
MEMORY_PATH = "memory/memory_store.json"

buffer_memory = ConversationBufferMemory(
    k = 5,
    memory_key= 'chat_history',
    return_messages= True
)

summary_memory = ConversationSummaryMemory (
    llm = llm,
    memory_key = "summary",
    return_messages = False
)


class HybridConversationMemory:
    def __init__ (self, max_turns  = 5, summary_trigger = 10):
        self.client = OpenAI(api_key=os.getenv("OPENAI_api_key"))
        self.max_turns = max_turns
        self.summary_trigger = summary_trigger
        self.buffer = deque (maxlen = max_turns)
        self.summary = ""
        self.turn_count = 0
        self._load_memory ()
    
    def _load_memory(self):
        if os.path.exists(MEMORY_PATH):
            try:
                with open(MEMORY_PATH, "r" , encoding = "utf-8") as f:
                    data = json.load(f)
                self.summary = data.get("summary" , "")
                self.buffer = deque(data.get("buffer" , []), maxlen =self.max_turns)
                self.turn_count = data.get("turn_count" , 0)
                print (f"[MEMORY] Loaded {len(self.buffer)} turns from disk")
            except Exception as e:
                print(f"[MEMORY] Failed to load memory: {e}")

    def _save_memory(self):
        try: 
            with open (MEMORY_PATH , "w" , encoding = "utf-8") as f:
                json.dump ({
                    "summary" : self.summary , 
                    "buffer" : list(self.buffer),
                    "turn_count" : self.turn_count  
                }, f, ensure_ascii=False , indent = 2)
        except Exception as e: 
            print (f"[MEMORY]  Failed to save memory: {e}")

    def save_context (self, user_query:str, assistant_response: str):
        self.buffer.append({"user " : user_query, "assistant" : assistant_response} )
        self.turn_count += 1

        if self.turn_count >= self.summary_trigger:
            self._summaraize_memory()
            self.buffer.clear()
            self.turn_count = 0

        self._save_memory()




    def load_context(self) -> str:
        buffer_text = "\n".join([f"user: {t['user']}\nAssistant: {t['assistant']}" for t in self.buffer])
        return f"Summary :\n{self.summary}\n\nRecent conversation :\n{buffer_text}"
    
    def _summaraize_memory(self)-> str:
        conversation_text = "\n".join([f"user: {t['user']}\nAssistant: {t['assistant']}" for t in self.buffer])
        prompt =  f"Summaraize the following medical conversation: \n\n{conversation_text}\n\nSummary"
    

        try:
            res = self.client.chat.completions.create(
                model = "gpt-3.5-turbo-0125",
                messages = [{"role" :  "user"  ,"content" : prompt}],
                temperature=0.1
            )
            summary_text = res.choices[0].message_content
            self.summary += "\n" + summary_text.strip()
        except Exception as e:
            print (f"[MEMORY] Summariation failed: {e}")
    
    def reset_memory (self):
        self.buffer.clear()
        self.summary = "" 
        self.turn_count  = 0
        if os.path.exists(MEMORY_PATH) :
            try:
                os.remove(MEMORY_PATH)
                print (f"[MEMORY] Memory reset succesfully")
            except Exception as e: 
                print (f"[MEMORY] Failed to delete memory file : {e}")

    