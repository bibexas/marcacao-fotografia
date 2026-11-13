import os
import warnings
from importlib import import_module
from pathlib import Path


def _load_dotenv():
	try:
		import_module("dotenv").load_dotenv()
		return
	except ImportError:
		pass

	env_file = Path.cwd() / ".env"
	if env_file.is_file():
		for line in env_file.read_text(encoding="utf-8").splitlines():
			line = line.strip()
			if not line or line.startswith("#") or "=" not in line:
				continue
			name, value = line.removeprefix("export ").split("=", 1)
			name = name.strip()
			value = value.strip().strip("\"'")
			if name:
				os.environ.setdefault(name, value)


_load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def _get_bool(name, default=False):
	value = os.getenv(name)
	if value is None:
		return default
	return value.strip().lower() in ("1", "true", "yes", "on")


def _warn_if_missing(name, value):
	if not value:
		warnings.warn(
			f"A variável de ambiente {name} não está definida.",
			RuntimeWarning,
			stacklevel=3,
		)


DATABASE_URL = os.getenv("DATABASE_URL")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
FLASK_DEBUG = _get_bool("FLASK_DEBUG")
WHATSAPP_PHONE = "".join(c for c in os.getenv("WHATSAPP_PHONE", "") if c.isdigit())

_warn_if_missing("DATABASE_URL", DATABASE_URL)
_warn_if_missing("FLASK_SECRET_KEY", FLASK_SECRET_KEY)
