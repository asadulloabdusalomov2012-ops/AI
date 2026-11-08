# Telegram Userbot + OpenRouter AI

A userbot that connects to your **real personal Telegram account** and auto-replies
to direct messages using a free AI model via OpenRouter.

## Files
- `main.py` — the userbot itself
- `generate_session.py` — run once to get a StringSession for Railway
- `system_prompt.txt` — edit this to change what the AI talks about / how it behaves
- `requirements.txt`, `Procfile` — for running and deploying

## 1. Get your Telegram API credentials
1. Go to https://my.telegram.org and log in with your phone number.
2. Click **API development tools**.
3. Fill the short form (App title/short name can be anything, e.g. "MyUserbot").
4. Copy your **App api_id** and **App api_hash**.

## 2. Get a free OpenRouter API key
1. Go to https://openrouter.ai and sign up / log in.
2. Open **Keys** in the dashboard.
3. Click **Create Key**, name it, and copy it (starts with `sk-or-v1-...`).

## 3. Run it locally first
```bash
pip install -r requirements.txt

# set these in your terminal session (or however you prefer)
export API_ID=123456
export API_HASH=your_api_hash
export PHONE_NUMBER=+998901234567
export OPENROUTER_API_KEY=sk-or-v1-...

python main.py
```
First run will ask for the SMS code sent to your Telegram app. After that, a local
`userbot_session.session` file keeps you logged in for future local runs.

## 4. Deploy to Railway
Railway's filesystem is wiped on every restart, so the local `.session` file won't
survive there. Instead, generate a **StringSession** once and store it as an
environment variable:

```bash
python generate_session.py
```
This logs in the same way (phone + SMS code) and prints a long string. Copy it.

### Railway setup
1. Push `main.py`, `generate_session.py`, `system_prompt.txt`, `requirements.txt`,
   and `Procfile` to a GitHub repo.
2. On https://railway.app: **New Project → Deploy from GitHub repo** → select the repo.
3. Open the service → **Variables** tab → add:
   - `API_ID`
   - `API_HASH`
   - `PHONE_NUMBER`
   - `OPENROUTER_API_KEY`
   - `TELEGRAM_SESSION` — the string you copied from `generate_session.py`
4. Railway detects the `Procfile` and runs the script as a background worker.
5. Check the **Logs** tab to see incoming/outgoing messages live.

## Customizing AI behavior
Just edit `system_prompt.txt` — no code changes needed. It's reloaded every time
the script starts.
