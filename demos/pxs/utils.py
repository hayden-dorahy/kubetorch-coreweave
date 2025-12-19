"""Utility functions for PXS demos."""

import os
import tomllib
from pathlib import Path

from dotenv import load_dotenv


def load_artifactory_creds() -> tuple[str, str]:
    """Load artifactory credentials.

    Priority:
    1. Environment variables (ARTIFACTORY_USER, ARTIFACTORY_TOKEN)
    2. .env.secrets file (loaded into env vars)
    3. uv credentials store (~/.local/share/uv/credentials/credentials.toml)

    Returns:
        (user, token)
    """
    # 1. Load from .env.secrets if present
    load_dotenv(".env.secrets")

    user = os.environ.get("ARTIFACTORY_USER")
    token = os.environ.get("ARTIFACTORY_TOKEN")

    if user and token:
        print("Using credentials from environment/.env.secrets")
        return user, token

    # 2. Fallback to uv credentials store
    print("Looking for credentials in uv store...")
    creds_file = Path.home() / ".local/share/uv/credentials/credentials.toml"

    if not creds_file.exists():
        raise FileNotFoundError(f"Credentials file not found at {creds_file} and env vars not set.")

    with open(creds_file, "rb") as f:
        data = tomllib.load(f)

    for cred in data.get("credential", []):
        if "physicsx.jfrog.io" in cred.get("service", ""):
            return cred["username"], cred["password"]

    raise ValueError("No PhysicsX artifactory credentials found in uv credentials or environment.")
