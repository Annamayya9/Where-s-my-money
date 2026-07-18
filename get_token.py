from __future__ import annotations

import tomllib
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from splitwise import Splitwise


def load_streamlit_secrets() -> dict:
    secrets_path = Path(".streamlit") / "secrets.toml"

    if not secrets_path.exists():
        raise FileNotFoundError(
            "Missing .streamlit/secrets.toml. Add your Splitwise credentials there first."
        )

    with secrets_path.open("rb") as file:
        return tomllib.load(file)


def extract_code_and_state(redirected_url: str) -> tuple[str, str | None]:
    parsed = urlparse(redirected_url)
    params = parse_qs(parsed.query)

    code_values = params.get("code")
    if not code_values:
        raise ValueError("Redirect URL does not contain a code query parameter.")

    state_values = params.get("state")
    return code_values[0], state_values[0] if state_values else None


def main() -> None:
    secrets = load_streamlit_secrets()

    consumer_key = secrets["SPLITWISE_CONSUMER_KEY"]
    consumer_secret = secrets["SPLITWISE_CONSUMER_SECRET"]
    redirect_uri = secrets.get("SPLITWISE_REDIRECT_URI", "http://localhost:8501")

    splitwise = Splitwise(consumer_key, consumer_secret)

    authorize_url, expected_state = splitwise.getOAuth2AuthorizeURL(redirect_uri)

    print("\nOpen this URL in your browser and approve the app:\n")
    print(authorize_url)
    print("\nAfter approval, copy the full redirected URL from your browser.")
    redirected_url = input("\nPaste redirected URL: ").strip()

    code, returned_state = extract_code_and_state(redirected_url)

    if returned_state and returned_state != expected_state:
        raise ValueError("OAuth state mismatch. Do not use this token.")

    token_payload = splitwise.getOAuth2AccessToken(code, redirect_uri)
    access_token = token_payload["access_token"]

    print("\nAdd this to Streamlit secrets:")
    print(f'\nSPLITWISE_ACCESS_TOKEN = "{access_token}"\n')


if __name__ == "__main__":
    main()
