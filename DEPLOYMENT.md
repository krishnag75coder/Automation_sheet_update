# 🌐 Deployment Guide: Production Task Entry Automation

This application is fully production-ready. You can deploy it to the cloud so anyone on your team can access it via a web link, or host it locally for your office network.

---

## 🚀 Option 1: Free Cloud Deployment on Render (Recommended)
*Render provides free hosting with automated SSL (HTTPS) and zero server maintenance.*

### Steps:
1. **Push this project folder to GitHub**:
   - Create a new repository on [GitHub](https://github.com).
   - In this folder, initialize and push:
     ```bash
     git init
     git add .
     git commit -m "Production automation ready for deploy"
     git branch -M main
     git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
     git push -u origin main
     ```
2. **Deploy on Render**:
   - Go to **[Render.com](https://render.com)** and sign in (free).
   - Click **New +** > **Web Service**.
   - Select your GitHub repository.
   - Render will automatically detect settings from [`render.yaml`](render.yaml) and [`Procfile`](Procfile):
     - **Environment**: `Python`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4`
   - Click **Deploy Web Service**.
3. **Done!**
   - Within 1–2 minutes, Render gives you a public URL (e.g. `https://production-task-entry.onrender.com`).
   - Anyone on your team can open this link on their laptop or phone and submit tasks directly!

---

## ⚡ Option 2: Serverless Deployment on Vercel
*Fast, global serverless hosting.*

1. Push your code to GitHub (as in Option 1).
2. Go to **[Vercel.com](https://vercel.com)** and sign in.
3. Click **Add New Project** and select your GitHub repo.
4. Vercel automatically detects [`vercel.json`](vercel.json).
5. Click **Deploy**. Your app is live with an instant `.vercel.app` URL.

---

## 🐳 Option 3: Docker Deployment
*Perfect for VPS, AWS ECS, Google Cloud Run, DigitalOcean, or private servers.*

### Using Docker directly:
```bash
# Build the container image
docker build -t production-sheet-automation .

# Run container
docker run -d -p 5000:5000 --name task_automation production-sheet-automation
```
Then visit: `http://localhost:5000`

### Using Docker Compose:
```bash
docker-compose up -d
```

---

## 🏢 Option 4: Local Office Network Sharing (No Cloud Needed)
*Allow anyone on the same Wi-Fi / office network to access the tool from their computer or phone.*

1. Run the app on your computer:
   ```bash
   python app.py
   ```
2. Find your computer's local IP address:
   - In PowerShell, run: `ipconfig`
   - Look for **IPv4 Address** (e.g. `192.168.1.45`).
3. Any colleague on the same Wi-Fi can now open their browser and visit:
   ```
   http://192.168.1.45:5000
   ```

---

## 🩺 Health Check & Monitoring

For cloud platforms and uptime checkers:
- Health check URL: `GET /health` (returns `{"status": "healthy"}`)
- Ping URL: `GET /ping`
