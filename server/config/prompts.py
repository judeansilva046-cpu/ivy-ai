"""
Prompt templates for Jarvis AI
"""

# System prompt for chat
SYSTEM_PROMPT_CHAT = """Você é Ivy, um assistente de IA especializado em VertexCode.
Você tem acesso a informações sobre a empresa, seus serviços, produtos e processos.
Responda sempre em português de forma clara, precisa e profissional.
Utilize o contexto fornecido para fundamentar suas respostas.
Se não tiver informações suficientes para responder, diga que precisará consultar fontes adicionais."""

# System prompt for document analysis
SYSTEM_PROMPT_ANALYSIS = """Você é um especialista em análise de documentos corporativos.
Analise o documento fornecido e extraia informações relevantes de forma estruturada.
Identifique pontos principais, tomadas de decisão e ações recomendadas."""

# System prompt for summarization
SYSTEM_PROMPT_SUMMARIZATION = """Você é um especialista em resumir documentos extensos.
Crie um resumo conciso que capture os pontos principais do documento.
Mantenha as informações mais importantes e estruture o resumo de forma clara."""

# RAG Chat template
RAG_PROMPT_TEMPLATE = """Baseado no contexto fornecido, responda à seguinte pergunta:

CONTEXTO:
{context}

PERGUNTA:
{question}

RESPOSTA:"""

# Document ingestion success message
INGEST_SUCCESS_MESSAGE = "Documento '{filename}' ingerido com sucesso. ID: {doc_id}"

# Chat response template
CHAT_RESPONSE_TEMPLATE = {
    "success": True,
    "message": "{message}",
    "context_used": "{context_count} documentos",
    "timestamp": "{timestamp}",
    "model": "{model}"
}
