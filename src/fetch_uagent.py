#!/usr/bin/env python3
"""
Fetch.ai uAgent wrapper for restaurant recommendations.

This keeps the existing recommendation logic unchanged by invoking:
  npx tsx src/agent/cli.ts "<query>"

Run:
  python src/fetch_uagent.py

Required:
  - MCP server running separately (npm run dev)
  - Node deps installed (npm install)
  - Python deps: pip install uagents
"""

from __future__ import annotations

import asyncio
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from uagents import Agent, Context, Model, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)


REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_PORT = int(os.getenv("FETCH_UAGENT_PORT", "8000"))
DEFAULT_NAME = os.getenv("FETCH_UAGENT_NAME", "restaurant_recommendation_uagent")
DEFAULT_SEED = os.getenv(
    "FETCH_UAGENT_SEED",
    "replace-this-with-your-own-strong-seed-phrase-please",
)
DEFAULT_ENDPOINT = os.getenv("FETCH_UAGENT_ENDPOINT", "").strip()
AGENTVERSE_API_KEY = os.getenv("AGENTVERSE_API_KEY", "").strip()
MAILBOX_ENABLED = os.getenv("FETCH_UAGENT_MAILBOX", "true").lower() in {
    "1",
    "true",
    "yes",
}


class RequestMessage(Model):
    text: str


class ResponseMessage(Model):
    text: str


class RecommendResult:
    def __init__(self, ok: bool, text: str):
        self.ok = ok
        self.text = text


def _clean_cli_output(raw: str) -> str:
    lines = [line.rstrip() for line in raw.splitlines()]
    filtered: list[str] = []
    for line in lines:
        if line.startswith("[dotenv@"):
            continue
        if line.startswith("> mcp-restaurant-booking@"):
            continue
        if line.startswith("> tsx "):
            continue
        filtered.append(line)
    # Keep blank lines to preserve paragraph spacing in chat UIs.
    while filtered and filtered[0] == "":
        filtered.pop(0)
    while filtered and filtered[-1] == "":
        filtered.pop()
    return "\n".join(filtered).strip()


def _run_recommender_cli(query: str) -> RecommendResult:
    cmd = ["npx", "tsx", "src/agent/cli.ts", query]
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        check=False,
    )

    if proc.returncode == 0:
        out = _clean_cli_output(proc.stdout)
        if out:
            return RecommendResult(ok=True, text=out)
        return RecommendResult(ok=False, text="Empty response from recommendation CLI.")

    err = _clean_cli_output(proc.stderr or proc.stdout)
    return RecommendResult(ok=False, text=err or "Recommendation CLI failed.")


async def recommend(query: str) -> RecommendResult:
    # Run subprocess off the event loop.
    return await asyncio.to_thread(_run_recommender_cli, query)


def _chat_text_message(text: str) -> ChatMessage:
    """
    ASI1 / Agent Chat Protocol style: markdown (e.g. ![alt](url)) renders in many clients.
    """
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=text)],
    )


agent_kwargs = {
    "name": DEFAULT_NAME,
    "seed": DEFAULT_SEED,
    "port": DEFAULT_PORT,
    "mailbox": MAILBOX_ENABLED,
}
if DEFAULT_ENDPOINT:
    # Optional explicit endpoint; leave unset for pure mailbox mode.
    agent_kwargs["endpoint"] = [DEFAULT_ENDPOINT]
if AGENTVERSE_API_KEY:
    # Lets the agent associate published details/manifests with your Agentverse account.
    agent_kwargs["agentverse"] = {"api_key": AGENTVERSE_API_KEY}

agent = Agent(**agent_kwargs)
protocol = Protocol(name="RestaurantRecommendationProtocol", version="1.0.0")
chat_protocol = Protocol(spec=chat_protocol_spec)

@agent.on_event("startup")
async def startup(ctx: Context) -> None:
    endpoint = f"http://127.0.0.1:{DEFAULT_PORT}"
    ctx.logger.info("uAgent started")
    ctx.logger.info("Name: %s", DEFAULT_NAME)
    ctx.logger.info("Address: %s", agent.address)
    ctx.logger.info("Port: %s", DEFAULT_PORT)
    ctx.logger.info("Local endpoint: %s", endpoint)
    ctx.logger.info("Mailbox enabled: %s", MAILBOX_ENABLED)
    if DEFAULT_ENDPOINT:
        ctx.logger.info("Advertised endpoint: %s", DEFAULT_ENDPOINT)
    ctx.logger.info("Ensure MCP server is running at http://127.0.0.1:3000/mcp")


@protocol.on_message(RequestMessage, replies=ResponseMessage)
async def handle_request(ctx: Context, sender: str, msg: RequestMessage) -> None:
    query = (msg.text or "").strip()
    if not query:
        await ctx.send(sender, ResponseMessage(text="Missing request text."))
        return

    result = await recommend(query)
    if result.ok:
        await ctx.send(sender, ResponseMessage(text=result.text))
    else:
        await ctx.send(
            sender, ResponseMessage(text=f"Failed to get recommendations: {result.text}")
        )


@chat_protocol.on_message(ChatAcknowledgement)
async def handle_chat_ack(
    ctx: Context, sender: str, msg: ChatAcknowledgement
) -> None:
    ctx.logger.info(
        "Got chat acknowledgement from %s for msg_id=%s",
        sender,
        msg.acknowledged_msg_id,
    )


@chat_protocol.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage) -> None:
    # Acknowledge receipt first (per AgentChatProtocol interaction pattern)
    if msg.msg_id:
        await ctx.send(
            sender,
            ChatAcknowledgement(
                timestamp=datetime.now(timezone.utc),
                acknowledged_msg_id=msg.msg_id,
            ),
        )

    query = msg.text().strip() if hasattr(msg, "text") else ""
    if not query:
        await ctx.send(sender, _chat_text_message("Please send a text query."))
        return

    result = await recommend(query)
    response_text = (
        result.text if result.ok else f"Failed to get recommendations: {result.text}"
    )
    await ctx.send(sender, _chat_text_message(response_text))


if __name__ == "__main__":
    # Publish protocol manifest metadata to make interactions discoverable.
    agent.include(protocol, publish_manifest=True)
    # Include the official AgentChatProtocol spec expected by Agentverse chat checks.
    agent.include(chat_protocol, publish_manifest=True)
    agent.run()
