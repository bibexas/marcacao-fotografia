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

if not DATABASE_URL:
	warnings.warn(
		"A variável de ambiente DATABASE_URL não está definida.",
		RuntimeWarning,
		stacklevel=2,
	)
