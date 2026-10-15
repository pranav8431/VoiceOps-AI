"use client";

import { useCallback, useState } from "react";
import { LiveKitRoom } from "@livekit/components-react";
import "@livekit/components-styles";
import VoiceAgent from "@/components/VoiceAgent";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export default function Home() {
  const [connectionState, setConnectionState] = useState<
    "idle" | "connecting" | "connected"
  >("idle");
  const [token, setToken] = useState<string>("");
  const [livekitUrl, setLivekitUrl] = useState<string>("");

  const connect = useCallback(async () => {
    setConnectionState("connecting");
    try {
      const res = await fetch(`${BACKEND_URL}/api/token`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ room: "voicd-room" }),
      });
      if (!res.ok) throw new Error(`Token request failed: ${res.status}`);
      const data = await res.json();
      setToken(data.token);
      setLivekitUrl(data.url);
      setConnectionState("connected");
    } catch (err) {
      console.error("Failed to connect:", err);
      setConnectionState("idle");
    }
  }, []);

  const disconnect = useCallback(() => {
    setToken("");
    setLivekitUrl("");
    setConnectionState("idle");
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <h1 className="mb-2 text-3xl font-bold tracking-tight">VoiceOps AI</h1>
      <p className="mb-10 text-neutral-500">
        Real-time voice assistant for HR &amp; payroll operations
      </p>

      {connectionState === "idle" && (
        <button
          onClick={connect}
          className="rounded-full bg-white px-8 py-3 text-sm font-semibold text-black transition hover:bg-neutral-200"
        >
          Start Conversation
        </button>
      )}

      {connectionState === "connecting" && (
        <div className="flex items-center gap-2 text-neutral-400">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-neutral-400 border-t-transparent" />
          Connecting...
        </div>
      )}

      {connectionState === "connected" && token && livekitUrl && (
        <div className="flex w-full max-w-lg flex-col items-center gap-6">
          <LiveKitRoom
            token={token}
            serverUrl={livekitUrl}
            connect={true}
            audio={true}
            onDisconnected={disconnect}
            className="w-full"
          >
            <VoiceAgent />
          </LiveKitRoom>

          <button
            onClick={disconnect}
            className="rounded-full border border-neutral-700 px-6 py-2 text-sm text-neutral-400 transition hover:border-neutral-500 hover:text-neutral-200"
          >
            End Conversation
          </button>
        </div>
      )}
    </main>
  );
}
