# Deploy PromptEditor on Railway

## Prerequisites

- [Railway](https://railway.app) account (sign up with GitHub)
- GitHub repo pushed (this project)
- API keys: **ElevenLabs**, **Groq**

---

## Step 1: Create a new project

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repo: `mananawasthi-cmd/PromptEditor`
5. **Critical – fix Railpack error:** Railway may default to Railpack and fail. Fix it:
   - Go to your **Service** → **Settings**
   - **Root Directory:** Must be **empty** (or `.`). If it shows `frontend`, clear it.
   - **Builder:** If there's a Builder dropdown, select **Dockerfile**
   - **Config file path** (optional): Set to `/railway.json` to force Dockerfile from repo root
6. Click **Redeploy** after changing settings

---

## Step 2: Add API keys (environment variables)

Railway injects env vars into your backend at runtime. **Never commit API keys to git.**

### How to add variables in Railway

1. Open your Railway project
2. Click your **service** (PromptEditor)
3. Go to the **Variables** tab (or **Settings** → **Variables**)
4. Click **"+ New Variable"** or **"Add Variable"**
5. Add each variable:

| Variable | Value | Where to get it |
|---------|-------|-----------------|
| `ELEVENLABS_API_KEY` | Your ElevenLabs API key | [elevenlabs.io](https://elevenlabs.io) → Profile → API Key |
| `GROQ_API_KEY` | Your Groq API key | [console.groq.com](https://console.groq.com) → API Keys → Create API Key |

6. Click **Add** for each. Railway saves automatically.
7. **Redeploy** after adding variables (Deployments → ⋮ → Redeploy)

### Optional variables

| Variable | Default | Use |
|---------|---------|-----|
| `GROQ_MODEL` | `openai/gpt-oss-120b` | Groq model for chat |
| `CORS_ORIGINS` | `*` | Leave unset in production |

### Getting your API keys

- **ElevenLabs:** Sign up at [elevenlabs.io](https://elevenlabs.io) → Profile (top right) → API Key
- **Groq:** Sign up at [console.groq.com](https://console.groq.com) → API Keys → Create API Key

---

## Step 3: Deploy

1. Railway builds and deploys automatically when you connect the repo
2. After the build finishes, click **"Settings"** → **"Generate Domain"**
3. Your app will be live at `https://your-app-name.up.railway.app`

---

## Step 4: Test

1. Open the generated URL
2. Log in with **AdminManan** / **Manan@123**
3. Try: Edit prompts, Listen (TTS), Chat, Voice Chat

---

## Troubleshooting

### Build fails
- Check the build logs in Railway
- Ensure `Dockerfile` and `railway.json` are in the repo root

### 502 Connection Refused
- **Remove custom target port**: In Railway → Settings → Networking → clear "Target port" (leave empty). Let Railway auto-detect from $PORT.
- Ensure deployment succeeded and app started (check Deployments → View logs).

### API errors (TTS, Chat)
- Verify `ELEVENLABS_API_KEY` and `GROQ_API_KEY` are set correctly
- Check Railway logs: **Deployments** → select deployment → **View Logs**

### Login not working
- Credentials are hardcoded in `LoginPage.vue`: AdminManan / Manan@123

---

## Cost

- Railway offers **$5 free credit** per month
- Usage-based after that (~$5–10/month for a small app)
- Add a payment method in **Account Settings** → **Billing**
