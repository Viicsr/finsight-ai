from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory as ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Store en memoria (en producción sería Redis o PostgreSQL)
store: dict[str, ChatMessageHistory] = {}


def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Eres un asistente del CRM bancario. Tienes acceso al historial de la conversación.",  # noqa: E501
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)


def print_history(session_id: str) -> None:
    history = store[session_id]
    print(f"\nSesión: {session_id}")
    print(f"Mensajes: {len(history.messages)}")

    for index, message in enumerate(history.messages, start=1):
        print(f"{index}. {message.type}: {message.content[:100]}")


chain = prompt | llm

# Envuelve el chain con gestión de historial automática
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# Simula una conversación de 3 turnos
session = {"configurable": {"session_id": "user_123"}}

turns = [
    "Tengo un cliente llamado María García con un saldo de 15.000€ en cuenta de inversión.",  # noqa: E501
    "¿Cuál sería el perfil de riesgo adecuado para ella?",
    "¿Y qué productos específicos le recomendarías de los que mencionaste antes?",
]

for turn in turns:
    response = chain_with_history.invoke({"input": turn}, config=session)
    print(f"Usuario: {turn}")
    print(f"Asistente: {response.content}\n")

# Ver cuántos tokens ocupa ya el historial
history = store["user_123"]
print(f"\nMensajes en historial: {len(history.messages)}")

other_session = {"configurable": {"session_id": "user_456"}}

response = chain_with_history.invoke(
    {"input": "¿Quién es María García?"},
    config=other_session,
)

print(response.content)
print_history("user_456")
