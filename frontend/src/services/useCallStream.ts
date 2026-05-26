// Gerçek zamanlı çağrı akışı için WebSocket hook'u.
// Backend'e /ws/calls üzerinden bağlanır, "new_call" mesajlarını dinler.
// Otomatik yeniden bağlanma + ping/pong canlılık kontrolü.

import { useEffect, useRef, useState } from "react";
import type { HelpCall } from "../types";

type WSMessage =
  | { type: "hello"; msg: string }
  | { type: "new_call"; call: HelpCall }
  | { type: "pong" };

export function useCallStream(onNewCall?: (call: HelpCall) => void) {
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const callbackRef = useRef(onNewCall);
  callbackRef.current = onNewCall;

  useEffect(() => {
    let cancelled = false;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let pingTimer: ReturnType<typeof setInterval> | null = null;

    const connect = () => {
      if (cancelled) return;
      const proto = window.location.protocol === "https:" ? "wss" : "ws";
      const url = `${proto}://${window.location.host}/ws/calls`;
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        // 25 sn'de bir ping atarak proxy timeout'larından kaçın
        pingTimer = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: "ping" }));
          }
        }, 25000);
      };

      ws.onclose = () => {
        setConnected(false);
        if (pingTimer) clearInterval(pingTimer);
        // 2 sn sonra yeniden bağlan
        if (!cancelled) {
          reconnectTimer = setTimeout(connect, 2000);
        }
      };

      ws.onerror = () => {
        ws.close();
      };

      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data) as WSMessage;
          if (data.type === "new_call" && callbackRef.current) {
            callbackRef.current(data.call);
          }
        } catch {
          // Geçersiz JSON ise sessizce yok say
        }
      };
    };

    connect();

    return () => {
      cancelled = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (pingTimer) clearInterval(pingTimer);
      wsRef.current?.close();
    };
  }, []);

  return { connected };
}
