"""WebSocket bağlantı yöneticisi.

Yeni çağrı geldiğinde tüm bağlı istemcilere JSON mesaj yayınlar.
Tek süreçli MVP için yeterli; çoklu worker için Redis pub/sub gerekli.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Aktif WebSocket bağlantılarını yönetir, broadcast yapar."""

    def __init__(self) -> None:
        self.active: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self.active.add(ws)
        logger.info("WS connect: total=%d", len(self.active))

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            self.active.discard(ws)
        logger.info("WS disconnect: total=%d", len(self.active))

    async def broadcast(self, payload: dict[str, Any]) -> None:
        """JSON payload'u tüm bağlı istemcilere gönder. Kopukları temizler."""
        if not self.active:
            return
        msg = json.dumps(payload, default=str, ensure_ascii=False)
        dead = []
        for ws in list(self.active):
            try:
                await ws.send_text(msg)
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                for ws in dead:
                    self.active.discard(ws)


manager = ConnectionManager()
