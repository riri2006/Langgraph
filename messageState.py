import langchain_core.messages as messages
from langchain_core.messages import HumanMessage

msg = HumanMessage(content="Hello Riddhi")

print(type(msg))
print(msg.content)
print(msg.type)
print(msg.id)
print(msg.model_dump())
print("\nDIR(MESSAGES):",dir(messages))

