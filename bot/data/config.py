"""Centralized bot configuration loader.

This module tries to read environment variables for the Telegram bot without
breaking the Django build steps (e.g. during ``collectstatic`` in a Docker
image build) where the secret ``.env`` file is often not copied into the
image (it's ignored by ``.dockerignore``) and environment variables from
``docker-compose.yml`` are NOT yet applied.

Key points:
1. We attempt to locate a .env file in a few likely locations (project root, bot/, current working dir).
2. We never hard‑fail if BOT_TOKEN is missing at import time; instead we provide
   a placeholder so that static collection and admin commands still work.
3. Runtime code that actually needs a valid token (sending telegram messages)
   should gracefully handle a placeholder / empty token.
"""

from __future__ import annotations

import os
from pathlib import Path
from environs import Env

env = Env()

# Candidate .env locations (ordered). We stop at the first existing file.
_CURRENT_FILE = Path(__file__).resolve()
_CANDIDATE_ENV_FILES = [
	_CURRENT_FILE.parents[2] / ".env",  # project root: <root>/.env
	_CURRENT_FILE.parents[1] / ".env",  # bot/.env (if someone places it there)
	Path.cwd() / ".env",                 # working directory
]
for _candidate in _CANDIDATE_ENV_FILES:
	try:
		if _candidate.is_file():
			env.read_env(_candidate)  # load and stop after first hit
			break
	except Exception:  # noqa: broad-except (defensive; ignore malformed files)
		pass

# Also read any process-level env already present (no-op if already loaded)
try:
	env.read_env()  # default behaviour: only reads if .env exists in CWD
except Exception:
	pass

def _get_bot_token() -> str:
	# Prefer real environment variable (e.g. provided by container runtime)
	token = os.getenv("BOT_TOKEN")
	if token:
		return token
	# Fallback to environs (with default) without throwing EnvError
	try:
		return env.str("BOT_TOKEN")
	except Exception:  # noqa
		return ""  # empty indicates missing


BOT_TOKEN = _get_bot_token() or "PLACEHOLDER_BOT_TOKEN"  # Bot token (may be placeholder during build)
ADMINS = os.getenv("ADMINS") or ",".join(env.list("ADMINS", default=[]))
if isinstance(ADMINS, str):
	# Normalize into list for downstream code expecting list
	ADMINS = [a.strip() for a in ADMINS.split(";") for a in a.split(",") if a.strip()]

# NOTE: Downstream code should check for a real token before attempting network calls.


