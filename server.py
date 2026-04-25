"""Remote MCP server: adult-joke tool + GenZ-word tool, behind HTTP Basic Auth."""
from __future__ import annotations

import base64
import os
import random
import secrets

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

mcp = FastMCP(
    "jokes-and-genz",
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)

ADULT_JOKES = [
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "My wife told me to stop impersonating a flamingo. I had to put my foot down.",
    "I asked my date if she liked cuddles. She said yes, so I gave her a Pokemon card.",
    "My girlfriend told me to take the spider out instead of killing it. We went and had drinks. Cool guy. Wants to be a web developer.",
    "I told my wife I was making a wine rack. She laughed. I built it anyway. Now she's the one whining.",
    "Marriage is like a deck of cards. In the beginning all you need is two hearts and a diamond. By the end you wish you had a club and a spade.",
    "My wife asked if she could have a little peace and quiet while she cooks dinner. So I took the battery out of the smoke alarm.",
    "I went to the doctor and said 'It hurts when I do this.' He said 'Don't do that.' Sent me a bill for $300.",
    "Behind every angry woman stands a man who has absolutely no idea what he did wrong.",
    "I bought my wife a fridge for her birthday. You should have seen her face light up when she opened it.",
]

GENZ_WORDS = {
    "rizz": "Charisma — especially the kind that helps you flirt successfully. Short for 'charisma'.",
    "bussin": "Really good, usually about food. 'This pizza is bussin' fr.'",
    "no cap": "No lie / for real. Used to emphasize honesty. Opposite: 'cap' = lie.",
    "slay": "To do something exceptionally well, or to look amazing. 'You slayed that fit.'",
    "delulu": "Delusional — usually self-aware about having unrealistic hopes. 'Delulu is the solulu.'",
    "mid": "Mediocre, average, underwhelming. A dismissive insult. 'That movie was mid.'",
    "ate": "Did something extremely well, with style. 'She ate and left no crumbs.'",
    "gyatt": "Exclamation of admiration, often (but not always) for an attractive figure.",
    "skibidi": "Nonsense slang from a viral series — used as a meaningless intensifier or ironically.",
    "ick": "A sudden turn-off in someone you were attracted to. 'He chewed loudly and that gave me the ick.'",
    "fr": "For real. Used for emphasis or agreement. 'That's wild fr.'",
    "lowkey": "Sort of / kinda / quietly. 'I lowkey want to leave.'",
    "highkey": "Openly / very much. Opposite of lowkey. 'I highkey love this song.'",
    "sigma": "A self-styled lone-wolf 'main character' archetype, often used ironically.",
    "npc": "Someone acting robotic, repetitive, or without independent thought — like a video-game NPC.",
    "bet": "OK / sure / agreed. 'Meet at 8?' 'Bet.'",
    "it's giving": "It has the vibe of ___. 'It's giving 2014 Tumblr.'",
    "based": "Admirably confident in an unpopular opinion; not caring what others think.",
    "cheugy": "Trying too hard or out of date — millennial-coded in a bad way.",
    "tea": "Gossip. 'Spill the tea.'",
}


@mcp.tool()
def adult_joke() -> str:
    """Return a random PG-13 adult joke (innuendo / wordplay, nothing explicit)."""
    return random.choice(ADULT_JOKES)


@mcp.tool()
def genz_word(word: str | None = None) -> dict:
    """Look up a GenZ slang word. If `word` is given, return its meaning;
    otherwise return a random word + meaning from the dictionary."""
    if word:
        key = word.lower().strip().lstrip("'").rstrip("'")
        if key in GENZ_WORDS:
            return {"word": key, "meaning": GENZ_WORDS[key]}
        return {"word": word, "meaning": "Not in dictionary."}
    key = random.choice(list(GENZ_WORDS.keys()))
    return {"word": key, "meaning": GENZ_WORDS[key]}


class BasicAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, username: str, password: str) -> None:
        super().__init__(app)
        token = base64.b64encode(f"{username}:{password}".encode()).decode()
        self._expected = f"Basic {token}"

    async def dispatch(self, request, call_next):
        auth = request.headers.get("authorization", "")
        if not secrets.compare_digest(auth, self._expected):
            return Response(
                "Unauthorized",
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="MCP"'},
            )
        return await call_next(request)


def build_app() -> Starlette:
    username = os.environ["MCP_USERNAME"]
    password = os.environ["MCP_PASSWORD"]
    app = mcp.streamable_http_app()
    app.add_middleware(BasicAuthMiddleware, username=username, password=password)
    return app


app = build_app()


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
