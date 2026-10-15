import os
import logging

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import AutoSubscribe, JobContext, JobProcess, WorkerOptions, cli, llm
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import deepgram, elevenlabs, silero
from livekit.plugins.openai import LLM as OpenAILLM

load_dotenv(dotenv_path="../.env")

logger = logging.getLogger("voicd-agent")

SYSTEM_PROMPT = """\
You are VoiceOps AI, a voice-operated assistant for HR, payroll, and labour-compliance operations.

Your capabilities:
- Answer questions about employee attendance, payroll, and compliance
- Look up applicable minimum wages, statutory requirements, and deadlines
- Create and manage support tickets and grievance reports
- Generate payroll exception reports and compliance summaries

Guidelines:
- Be concise. You are a voice agent — keep responses under 3 sentences unless the user asks for detail.
- When you don't have enough information, ask a clarifying question instead of guessing.
- For any action that modifies data, confirm with the user before executing.
- Always state what you did after completing an action so the user can verify.
- If a request is outside your capabilities, say so clearly.
"""


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(role="system", text=SYSTEM_PROMPT)

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    participant = await ctx.wait_for_participant()
    logger.info(f"Participant joined: {participant.identity}")

    agent = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        llm=OpenAILLM(
            model="llama-3.3-70b-versatile",
            base_url="https://api.groq.com/openai/v1",
            api_key=os.environ["GROQ_API_KEY"],
        ),
        tts=elevenlabs.TTS(
            voice_id="JBFqnCBsd6RMkjVDRZzb",  # "George" — professional male voice
            model_id="eleven_turbo_v2",
        ),
        chat_ctx=initial_ctx,
    )

    agent.start(ctx.room, participant)

    await agent.say(
        "Hello, I'm VoiceOps AI. How can I help you with HR or payroll today?",
        allow_interruptions=True,
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        )
    )
