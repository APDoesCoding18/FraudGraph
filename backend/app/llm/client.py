from openai import AsyncOpenAI
from app.core.config import settings

# Initialize AsyncOpenAI client targeting Ollama or OpenAI
llm_client = AsyncOpenAI(
    base_url=settings.OLLAMA_BASE_URL,
    api_key=settings.OLLAMA_API_KEY
)

async def generate_response(system_prompt: str, user_query: str, history: list[dict], model: str = settings.OLLAMA_MODEL) -> str:
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add history
    for msg in history:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        
    # Add latest query
    messages.append({"role": "user", "content": user_query})
    
    response = await llm_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0
    )
    
    return response.choices[0].message.content
