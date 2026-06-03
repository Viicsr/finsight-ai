from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# --- PATRÓN 1: PromptTemplate básico ---
template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Eres un analista financiero senior. Responde siempre en {language}.",
        ),
        (
            "human",
            "Analiza el siguiente cliente: nombre={client_name}, saldo={balance}€, tipo_cuenta={account_type}",
        ),  # noqa: E501
    ]
)

parser = StrOutputParser()

# LCEL: chain como pipeline
chain = template | llm | parser

result = chain.invoke(
    {
        "language": "español",
        "client_name": "María García",
        "balance": 15000,
        "account_type": "inversión",
    }
)
print("=== Análisis de cliente ===")
print(result)


# --- PATRÓN 2: Structured Output con Pydantic ---
class ClientRiskProfile(BaseModel):
    risk_level: str = Field(description="low, medium, or high")
    reasoning: str = Field(description="Explicación en máx 50 palabras")
    recommended_products: list[str] = Field(
        description="Lista de 2-3 productos recomendados"
    )  # noqa: E501


structured_llm = llm.with_structured_output(ClientRiskProfile)

structured_chain = template | structured_llm

result_structured = structured_chain.invoke(
    {
        "language": "español",
        "client_name": "Carlos López",
        "balance": 500,
        "account_type": "corriente",
    }
)
print("\n=== Perfil de riesgo estructurado ===")
print(f"Nivel de riesgo: {result_structured.risk_level}")
print(f"Razonamiento: {result_structured.reasoning}")
print(f"Productos recomendados: {result_structured.recommended_products}")
