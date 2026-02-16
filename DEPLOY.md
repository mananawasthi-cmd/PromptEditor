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
5. Railway will detect the `Dockerfile` and start building

---

## Step 2: Add environment variables

1. In your Railway project, click on your service
2. Go to the **Variables** tab
3. Add these variables:

| Variable | Description | Where to get it |
|----------|-------------|-----------------|
| `ELEVENLABS_API_KEY` | TTS (Listen) | [elevenlabs.io](https://elevenlabs.io) → Profile → API Key |
| `GROQ_API_KEY` | AI chat & translate | [console.groq.com](https://console.groq.com) → API Keys |

4. Optional: `CORS_ORIGINS` – leave unset in production (defaults to allow all)

---

## Step 3: Deploy

1. Railway builds and deploys automatically when you connect the repo
2. After the build finishes, click **"Settings"** → **"Generate Domain"**
3. Your app will be live at `https://your-app-name.up.railway.app`

---

## Step 4: Test

1. Open the generated URL
2. Log in with **AdminManan** / **Manan@123**
3. Try: Edit prompts, Listen (TTS), Chat, Translate, Voice Chat

---

## Troubleshooting

### Build fails
- Check the build logs in Railway
- Ensure `Dockerfile` and `railway.json` are in the repo root

### API errors (TTS, Chat, Translate)
- Verify `ELEVENLABS_API_KEY` and `GROQ_API_KEY` are set correctly
- Check Railway logs: **Deployments** → select deployment → **View Logs**

### Login not working
- Credentials are hardcoded in `LoginPage.vue`: AdminManan / Manan@123

---

## Cost

- Railway offers **$5 free credit** per month
- Usage-based after that (~$5–10/month for a small app)
- Add a payment method in **Account Settings** → **Billing**
