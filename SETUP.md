# Setup Guide

## Prerequisites

### Install Node.js (required for frontend)

If you see `zsh: command not found: npm`, Node.js is not installed.

**Option A – Download installer (recommended):**
1. Go to [https://nodejs.org](https://nodejs.org)
2. Download the **LTS** version
3. Run the `.pkg` installer and follow the prompts
4. **Close and reopen your terminal** (or run `source ~/.zshrc`)

**Option B – Homebrew:**
```bash
brew install node
```

**Option C – nvm (Node Version Manager):**
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# Load nvm (run this in each new terminal, or fix .zshrc permissions first)
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Install Node.js
nvm install 24

# Verify
node -v   # v24.13.1
npm -v    # 11.8.0
```

**If you get `permission denied: .zshrc`** – your `.zshrc` is owned by root. Fix it:
```bash
sudo chown $(whoami) ~/.zshrc
```
Then add nvm to `.zshrc`:
```bash
echo 'export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.zshrc
source ~/.zshrc
```

**Verify installation:**
```bash
node -v   # should show e.g. v20.x.x
npm -v    # should show e.g. 10.x.x
```

---

## Run the app

### Frontend only (works with mock data, no backend needed)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. If the backend is offline, the app uses local mock data.

### With backend (full stack)

**Terminal 1 – start backend:**
```bash
cd backend
./install.sh          # first time only
source venv/bin/activate
python run.py
```

**Terminal 2 – start frontend:**
```bash
cd frontend
npm install           # first time only
npm run dev
```

Open **http://localhost:5173**. The frontend proxies `/api` to the backend at `http://127.0.0.1:5000`.

### TTS (Listen to prompt)

1. Copy `backend/.env.example` to `backend/.env`
2. Add your ElevenLabs API key: `ELEVENLABS_API_KEY=your_key`
3. Restart the backend
4. In the editor: select text → enter Voice ID → click Play

Example Voice ID: `JBFqnCBsd6RMkjVDRZzb` (from ElevenLabs docs)

### Connection failed?

- Ensure the backend is running: `cd backend && source venv/bin/activate && python run.py`
- The app falls back to mock data when the backend is offline

### npm install shows only a spinner (no output)?

Try verbose mode to see what's happening:
```bash
npm install --loglevel verbose
```

If you see `SELF_SIGNED_CERT_IN_CHAIN`, the project has an `.npmrc` that disables strict SSL. Just run:
```bash
npm install
```
It will use the project's `.npmrc` (strict-ssl=false) automatically.
