"""RAG pipeline for the music recommender using Claude."""
import csv
import os
import subprocess
from pathlib import Path
from typing import Optional

import anthropic


def _get_anthropic_client() -> Optional[anthropic.Anthropic]:
    """Return an Anthropic SDK client when API credentials are available."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return anthropic.Anthropic(api_key=api_key)

    auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")
    if auth_token:
        return anthropic.Anthropic(auth_token=auth_token)

    # CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR carries the OAuth token, but the
    # FD is close-on-exec so child processes can't read it. Fall back to None
    # and let callers use the CLI path instead.
    return None


def _query_via_cli(question: str, system: str) -> str:
    """Use the `claude` CLI (already authenticated via Claude Code) to answer."""
    # Run from /tmp so claude doesn't discover the project's CLAUDE.md and
    # trigger tool calls that would exhaust --max-turns before the model responds.
    result = subprocess.run(
        [
            "claude", "--print",
            "--output-format", "text",
            "--max-turns", "1",
            "--system-prompt", system,
        ],
        input=question,
        capture_output=True,
        text=True,
        timeout=120,
        cwd="/tmp",
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {result.stderr.strip()}")
    return result.stdout.strip()


def load_songs_as_context(csv_path: str) -> str:
    """Format the songs CSV as a plain-text block for use as RAG context."""
    lines = []
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            lines.append(
                f"- {row['title']} by {row['artist']} | genre={row['genre']} | "
                f"mood={row['mood']} | energy={row['energy']} | "
                f"tempo={row['tempo_bpm']} BPM | valence={row['valence']} | "
                f"danceability={row['danceability']} | acousticness={row['acousticness']}"
            )
    return "\n".join(lines)


def query_rag(question: str, csv_path: Optional[str] = None) -> str:
    """Answer a natural-language question about the music catalog using Claude."""
    if csv_path is None:
        csv_path = str(Path(__file__).parent.parent / "data" / "songs.csv")

    context = load_songs_as_context(csv_path)
    system = (
        "You are a music recommender assistant. "
        "Use only the song catalog below to answer questions. "
        "Do not invent songs that are not listed.\n\n"
        f"Song catalog:\n{context}"
    )

    client = _get_anthropic_client()
    if client is not None:
        message = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": question}],
        )
        return message.content[0].text

    # No SDK credentials available — use the authenticated claude CLI instead
    return _query_via_cli(question, system)


if __name__ == "__main__":
    answer = query_rag("Which songs are best for studying or focusing?")
    print(answer)
