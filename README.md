# Splitwise Monthly Credit-Card Spending

A small Streamlit app that connects to the Splitwise API and calculates monthly credit-card spending based on expenses where you paid upfront.

## What It Calculates

For the selected month and year, the app fetches Splitwise expenses using pagination and includes only expenses where:

- the expense is not deleted
- `payment == true` records are ignored
- the current user's `paid_share` is greater than zero

Totals shown:

- total paid upfront
- actual personal spending, calculated from `owed_share`
- amount others owe back, calculated as `paid_share - owed_share`

All money calculations use Python `Decimal`.

## Setup

1. Create a virtual environment.

```bash
python -m venv .venv
```

2. Activate it.

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Create `.streamlit/secrets.toml`.

```toml
SPLITWISE_CONSUMER_KEY = "your_consumer_key"
SPLITWISE_CONSUMER_SECRET = "your_consumer_secret"
SPLITWISE_REDIRECT_URI = "http://localhost:8501"
SPLITWISE_ACCESS_TOKEN = "replace_after_running_get_token"
```

Use the consumer key and consumer secret from your registered Splitwise app. Do not commit this file.

5. Generate a Splitwise OAuth2 access token.

```bash
python get_token.py
```

Open the printed authorization URL, approve the app, then paste the full redirected URL back into the terminal. Copy the printed `SPLITWISE_ACCESS_TOKEN` value into `.streamlit/secrets.toml`.

6. Run the app.

```bash
streamlit run app.py
```

## Hosting on Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. Do not commit `.streamlit/secrets.toml` with a real token.
3. Go to <https://streamlit.io/cloud> and sign in with GitHub.
4. Create a new app from the repository.
5. Set the main file path to `app.py`.
6. Add this secret in the app's Streamlit settings:

```toml
SPLITWISE_ACCESS_TOKEN = "your_real_splitwise_access_token"
```

7. Deploy the app.

## Project Structure

```txt
.
â”œâ”€â”€ app.py
â”œâ”€â”€ splitwise_client.py
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ README.md
â”œâ”€â”€ .gitignore
â””â”€â”€ .streamlit/
    â””â”€â”€ secrets.toml
```

