# routers/chat.py
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from uuid import UUID
import json

from apps.backend.services.llm_client import LLMClient
from apps.backend.routers.deps import get_auth_headers
from apps.backend.models.schemas import POST_chat
# from apps.backend.services.history import (
#     get_recent_messages, save_message, count_messages
# )
# from apps.backend.services.memory import get_memory, summarize_session

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/")
async def post_chat(
    req:     POST_chat,
    headers: dict = Depends(get_auth_headers)
):
    token = headers["Authorization"].replace("Bearer ", "")
    llm   = LLMClient(token=token)

    async def stream():
        recent_messages = await get_recent_messages(req.session_id, limit=5)
        system_prompt   = _build_system_prompt()

        messages = [
            {"role": "system", "content": system_prompt},
            *recent_messages,
            {"role": "user",   "content": req.message}
        ]

        full_response = ""
        async for token in llm.chat_stream(task="chat_1", messages=messages):
            full_response += token
            yield f"data: {json.dumps({'token': token})}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"

        await save_message(req.session_id, "user",      req.message)
        await save_message(req.session_id, "assistant", full_response)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":     "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


def _build_system_prompt() -> str:
    return """คุณคือ TDET Chatbot ผู้เชี่ยวชาญด้าน SW/HW ยานพาหนะ
ตอบจาก context ที่ให้เท่านั้น
ถ้าไม่มีข้อมูลใน context ให้บอกว่า "ไม่พบข้อมูลในระบบ"
ห้าม hallucinate เด็ดขาด"""