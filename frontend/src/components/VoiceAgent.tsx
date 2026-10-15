"use client";

import {
  useVoiceAssistant,
  BarVisualizer,
  RoomAudioRenderer,
  VoiceAssistantControlBar,
  useTrackTranscription,
} from "@livekit/components-react";
import { Track } from "livekit-client";
import { useEffect, useRef } from "react";

function TranscriptionView({
  transcriptions,
  label,
}: {
  transcriptions: { id: string; text: string; final: boolean }[];
  label: string;
}) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    containerRef.current?.scrollTo({
      top: containerRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [transcriptions]);

  return (
    <div className="flex flex-col gap-1">
      <span className="text-xs uppercase tracking-wide text-neutral-500">
        {label}
      </span>
      <div
        ref={containerRef}
        className="h-32 overflow-y-auto rounded-lg bg-neutral-900 p-3 text-sm"
      >
        {transcriptions.map((t) => (
          <p
            key={t.id}
            className={t.final ? "text-neutral-200" : "text-neutral-500"}
          >
            {t.text}
          </p>
        ))}
      </div>
    </div>
  );
}

export default function VoiceAgent() {
  const { state, audioTrack, agentTranscriptions } = useVoiceAssistant();

  const userAudioTrack = useTrackTranscription({
    publication: undefined,
    source: Track.Source.Microphone,
  });

  const stateLabel: Record<string, string> = {
    disconnected: "Disconnected",
    connecting: "Connecting...",
    initializing: "Initializing...",
    listening: "Listening",
    thinking: "Thinking...",
    speaking: "Speaking",
  };

  return (
    <div className="flex flex-col items-center gap-8">
      <div className="flex flex-col items-center gap-3">
        <div className="h-24 w-64">
          <BarVisualizer
            state={state}
            barCount={5}
            trackRef={audioTrack}
            className="h-full w-full"
          />
        </div>
        <span className="text-sm font-medium text-neutral-400">
          {stateLabel[state] ?? state}
        </span>
      </div>

      <div className="w-full max-w-md space-y-4">
        <TranscriptionView
          transcriptions={agentTranscriptions}
          label="Agent"
        />
        <TranscriptionView
          transcriptions={userAudioTrack.segments}
          label="You"
        />
      </div>

      <VoiceAssistantControlBar />
      <RoomAudioRenderer />
    </div>
  );
}
