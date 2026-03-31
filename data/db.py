"""
OpenNemesis - Persistencia de Historial
Módulo SQLite async para guardar historial de conversación
"""

import aiosqlite
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

logger = logging.getLogger("OpenNemesis.DB")

DB_PATH = Path("data/conversations.db")

# Pool de conexiones (simple - una conexión por operación)
_db_connection: Optional[aiosqlite.Connection] = None


async def init_db():
    """Inicializa la base de datos y crea la tabla si no existe"""
    global _db_connection
    
    try:
        # Crear directorio si no existe
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        _db_connection = await aiosqlite.connect(DB_PATH)
        
        await _db_connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await _db_connection.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON messages(user_id)")
        
        await _db_connection.commit()
        
        logger.info(f"✓ Base de datos inicializada (async): {DB_PATH}")
    except Exception as e:
        logger.error(f"✗ Error inicializando base de datos: {e}")
        raise


async def close_db():
    """Cierra la conexión a la base de datos"""
    global _db_connection
    
    if _db_connection:
        await _db_connection.close()
        _db_connection = None


async def save_message(user_id: str, role: str, content: str):
    """Guarda un mensaje en la base de datos para un usuario específico (async)"""
    global _db_connection
    
    try:
        conn = _db_connection or await aiosqlite.connect(DB_PATH)
        is_local_conn = _db_connection is None
        
        await conn.execute(
            "INSERT INTO messages (user_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (user_id, role, content, datetime.now().isoformat())
        )
        
        await conn.commit()
        
        if is_local_conn:
            await conn.close()
        
        # logger.info(f"DB: Guardado mensaje para user_id={user_id}, role={role}")
    except Exception as e:
        logger.error(f"✗ Error guardando mensaje: {e}")


async def get_history(user_id: str, limit: int = 50) -> list:
    """Obtiene los últimos N mensajes del historial de un usuario (async)"""
    global _db_connection
    
    try:
        conn = _db_connection or await aiosqlite.connect(DB_PATH)
        is_local_conn = _db_connection is None
        
        cursor = await conn.execute(
            "SELECT role, content FROM messages WHERE user_id = ? ORDER BY id ASC LIMIT ?",
            (user_id, limit)
        )
        
        rows = await cursor.fetchall()
        
        if is_local_conn:
            await conn.close()
        
        return [{"role": m[0], "content": m[1]} for m in rows]
    except Exception as e:
        logger.error(f"✗ Error obteniendo historial: {e}")
        return []


async def clear_history(user_id: str) -> int:
    """Borra los mensajes del historial de un usuario específico (async)"""
    global _db_connection
    
    try:
        conn = _db_connection or await aiosqlite.connect(DB_PATH)
        is_local_conn = _db_connection is None
        
        cursor = await conn.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
        
        await conn.commit()
        deleted_count = cursor.rowcount
        
        if is_local_conn:
            await conn.close()
        
        logger.info(f"✓ Historial borrado para usuario {user_id}: {deleted_count} mensajes eliminados")
        return deleted_count
    except Exception as e:
        logger.error(f"✗ Error borrando historial: {e}")
        return 0


async def get_message_count(user_id: str) -> int:
    """Retorna el número de mensajes de un usuario específico (async)"""
    global _db_connection
    
    try:
        conn = _db_connection or await aiosqlite.connect(DB_PATH)
        is_local_conn = _db_connection is None
        
        cursor = await conn.execute("SELECT COUNT(*) FROM messages WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        
        if is_local_conn:
            await conn.close()
        
        return row[0] if row else 0
    except Exception as e:
        logger.error(f"✗ Error contando mensajes: {e}")
        return 0


async def get_total_message_count() -> int:
    """Retorna el número total de mensajes en la base de datos (async)"""
    global _db_connection
    
    try:
        conn = _db_connection or await aiosqlite.connect(DB_PATH)
        is_local_conn = _db_connection is None
        
        cursor = await conn.execute("SELECT COUNT(*) FROM messages")
        row = await cursor.fetchone()
        
        if is_local_conn:
            await conn.close()
        
        return row[0] if row else 0
    except Exception as e:
        logger.error(f"✗ Error contando mensajes: {e}")
        return 0


def format_history_for_context(messages: list, max_messages: int = 20) -> str:
    """
    Formatea el historial de mensajes para incluirlo en las instrucciones del agente.
    
    Args:
        messages: Lista de mensajes del historial
        max_messages: Máximo número de mensajes a incluir
        
    Returns:
        String formateado con el historial
    """
    if not messages:
        return ""
    
    # Limitar a los últimos max_messages
    recent_messages = messages[-max_messages:]
    
    history_lines = []
    for msg in recent_messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        # Truncar mensajes muy largos
        if len(content) > 500:
            content = content[:497] + "..."
        
        if role == "user":
            history_lines.append(f"Usuario: {content}")
        else:
            history_lines.append(f"Asistente: {content}")
    
    if history_lines:
        return "\n".join([
            "",
            "=== HISTORIAL DE CONVERSACIÓN ANTERIOR ===",
            *history_lines,
            "==========================================="
        ])
    
    return ""



