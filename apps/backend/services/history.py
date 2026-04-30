# apps/backend/services/history.py
from uuid import UUID
from apps.backend.database import db


async def get_recent_messages(session_id: UUID, limit: int = 5) -> list:
    """ดึง messages ล่าสุดสำหรับ inject ใน prompt"""
    rows = await db.fetch("""
        SELECT role, content
        FROM messages
        WHERE session_id = $1
        ORDER BY created_at DESC
        LIMIT $2
    """, session_id, limit)

    # reverse กลับให้เรียงจากเก่า → ใหม่
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


async def save_message(
    session_id: UUID,
    role:       str,
    content:    str,
    sources:    list = None
) -> None:
    """บันทึก message ลง DB"""
    await db.execute("""
        INSERT INTO messages (session_id, role, content, sources)
        VALUES ($1, $2, $3, $4)
    """, session_id, role, content, sources)

    # update session updated_at
    await db.execute("""
        UPDATE chat_sessions
        SET updated_at = NOW()
        WHERE id = $1
    """, session_id)


async def count_messages(session_id: UUID) -> int:
    """นับจำนวน messages ใน session สำหรับ trigger summarize"""
    row = await db.fetchrow("""
        SELECT COUNT(*) as count
        FROM messages
        WHERE session_id = $1
    """, session_id)
    return row["count"]


async def get_all_messages(session_id: UUID) -> list:
    """ดึง messages ทั้งหมด ใช้ตอน summarize"""
    rows = await db.fetch("""
        SELECT role, content
        FROM messages
        WHERE session_id = $1
        ORDER BY created_at ASC
    """, session_id)
    return [{"role": r["role"], "content": r["content"]} for r in rows]