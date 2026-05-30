import tiktoken
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()

# gpt-4o-mini: barato, rápido, suficiente para desarrollo
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Contar tokens ANTES de llamar — control de costes
enc = tiktoken.encoding_for_model("gpt-4o-mini")

system_prompt = (
    "Eres un asistente financiero especializado en análisis de CRM bancario."  # noqa: E501
)
user_prompt = (
    "¿Qué métricas son más relevantes para evaluar la salud de una cartera de clientes?"  # noqa: E501
)

messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

# Calcular tokens antes de llamar
total_tokens = sum(len(enc.encode(m.content)) for m in messages)
print(f"Tokens estimados de entrada: {total_tokens}")
print(f"Coste estimado: ~${total_tokens * 0.00000015:.6f} (input gpt-4o-mini)")

# Llamada real
response = llm.invoke(messages)

print(f"\nRespuesta: {response.content}")
print(f"\nTokens reales usados: {response.response_metadata.get('token_usage', {})}")
