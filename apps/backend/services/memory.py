# apps/backend/services/memory.py
from uuid import UUID
from apps.backend.database import db


async def get_memory(session_id: UUID) -> str | None:
    """
    ดึง memory ของ session
    ตอนนี้ยังไม่มี login → ใช้ session_id แทน user_id
    """
    row = await db.fetchrow("""
        SELECT content
        FROM session_memories
        WHERE session_id = $1
    """, session_id)
    return row["content"] if row else None


async def summarize_session(session_id: UUID, llm) -> None:
    """
    สรุปบทสนทนาแล้วเก็บไว้
    เรียกทุก 20 messages หรือตอนลบ session
    """
    from apps.backend.services.history import get_all_messages

    messages = await get_all_messages(session_id)
    if len(messages) < 3:
        return  # session สั้นเกิน ไม่ต้อง summarize

    # สร้าง conversation text
    conv_text = "\n".join([
        f"{m['role']}: {m['content']}" for m in messages
    ])

    # ให้ LLM สรุป
    summary = await llm.chat(
        task="chat_1",
        messages=[
            {
                "role": "system",
                "content": """สรุปบทสนทนานี้เป็น bullet points ไม่เกิน 5 ข้อ
                             เน้น: ถามเรื่องอะไรบ่อย, topic หลัก,
                             context งาน, คำถามที่ยังค้างอยู่"""
            },
            {
                "role": "user",
                "content": f"บทสนทนา:\n{conv_text}"
            }
        ]
    )

    # upsert memory
    await db.execute("""
        INSERT INTO session_memories (session_id, content)
        VALUES ($1, $2)
        ON CONFLICT (session_id)
        DO UPDATE SET content = $2, updated_at = NOW()
    """, session_id, summary)