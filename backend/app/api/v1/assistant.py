from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.schemas.assistant import AssistantRequest, AssistantResponse
from app.repositories.case import get_case
from app.llm.client import generate_response
from app.graph.queries import graph_queries

router = APIRouter()

SYSTEM_PROMPT = """
You are an expert fraud investigation assistant for a financial institution. 
You analyze provided case context, including alerts, linked accounts, and transactions.
Be concise, clear, and highlight any suspicious patterns you see.
Do NOT make up data; base your answers strictly on the context provided.
"""

@router.post("/chat", response_model=AssistantResponse)
async def chat_assistant(
    request: AssistantRequest,
    db: AsyncSession = Depends(get_db)
):
    context_str = "No case context provided."
    sources = []

    if request.case_id:
        case = await get_case(db, request.case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Build context
        alerts_ctx = [
            f"Alert {a.id}: Score {a.risk_score}, Level {a.risk_level}, Rules {a.triggered_rules}"
            for a in case.alerts
        ]
        
        notes_ctx = [
            f"Note by {n.investigator_id}: {n.content}" for n in case.notes
        ]
        
        # We could run Cypher queries here to enrich the context
        # For example, checking if any account in the case is part of a suspicious cluster
        cluster_info = []
        for account in case.accounts:
            is_suspicious = await graph_queries.detect_suspicious_cluster(account.id)
            if is_suspicious:
                cluster_info.append(f"Account {account.id} is part of a suspicious graph cluster.")
                
        context_parts = [
            f"Case ID: {case.id}",
            f"Status: {case.status}",
            f"Alerts: {'; '.join(alerts_ctx) if alerts_ctx else 'None'}",
            f"Notes: {'; '.join(notes_ctx) if notes_ctx else 'None'}",
            f"Graph Insights: {'; '.join(cluster_info) if cluster_info else 'None'}"
        ]
        
        context_str = "\\n".join(context_parts)
        sources.append(f"Case {case.id}")

    prompt = f"""
    Context:
    {context_str}
    """

    history_dicts = [{"role": msg.role, "content": msg.content} for msg in request.history]

    # Call LLM
    try:
        answer = await generate_response(
            system_prompt=SYSTEM_PROMPT + prompt,
            user_query=request.query,
            history=history_dicts
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")

    return AssistantResponse(answer=answer, sources=sources)
