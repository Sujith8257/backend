# Railway Deployment Checklist

## Pre-Deployment Checklist

### ✅ Files Verified

1. **Procfile** ✅
   - Uses `wsgi:app` (correct)
   - Uses `$PORT` environment variable
   - Has proper gunicorn configuration

2. **railway.json** ✅
   - Uses `wsgi:app` (correct)
   - Uses NIXPACKS builder
   - Has proper start command

3. **wsgi.py** ✅
   - Starts scheduler on import
   - Generates initial article
   - Handles errors gracefully

4. **requirements.txt** ✅
   - All dependencies listed
   - Includes gunicorn
   - Includes supabase client

5. **api.py** ✅
   - No hardcoded paths
   - Uses environment variables
   - No file system writes (except in local mode)

## Required Environment Variables

Set these in Railway Dashboard → Variables:

```
GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key_here
FRONTEND_URL=https://your-frontend.vercel.app (or your frontend URL)
PORT=5000 (Railway sets this automatically)
FLASK_ENV=production (optional, but recommended)
```

**Important Notes:**
- Use **service_role** key for `SUPABASE_KEY`, NOT the anon key
- `PORT` is automatically set by Railway, but you can verify it
- `FRONTEND_URL` should match your frontend domain exactly

## Railway Configuration

### 1. Root Directory
- Go to Railway Dashboard → Your Service → Settings
- Set **Root Directory** to: `MODEL`

### 2. Build Settings
- Builder: **Nixpacks** (auto-detected)
- Build Command: Auto-detected from `requirements.txt`
- Start Command: Uses `Procfile` or `railway.json`

### 3. Deploy Settings
- Auto-deploy: Enabled (deploys on git push)
- Health Check: Optional (can use `/api/health`)

## Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Railway deployment"
   git push
   ```

2. **Railway Auto-Deploys**
   - Railway detects the push
   - Builds the application
   - Deploys automatically

3. **Check Logs**
   - Go to Railway Dashboard → Your Service → Logs
   - Look for:
     - ✅ "Supabase client initialized successfully"
     - ✅ "Background scheduler started in production mode"
     - ✅ "Generating initial article on startup..."

4. **Test Health Endpoint**
   ```
   GET https://your-app.railway.app/api/health
   ```
   Should return: `{"status": "healthy"}`

## Common Issues and Fixes

### Issue: Build Fails

**Possible Causes:**
- Missing dependencies in `requirements.txt`
- Python version mismatch
- Build timeout

**Solutions:**
- Check Railway logs for specific error
- Verify all dependencies are in `requirements.txt`
- Check `runtime.txt` specifies correct Python version

### Issue: App Crashes on Startup

**Possible Causes:**
- Missing environment variables
- Supabase connection fails
- Port configuration issue

**Solutions:**
- Check Railway logs for error messages
- Verify all environment variables are set
- Check Supabase credentials are correct

### Issue: Scheduler Not Running

**Possible Causes:**
- `wsgi.py` not being used
- Thread not starting
- Error in scheduler function

**Solutions:**
- Verify `Procfile` uses `wsgi:app`
- Check Railway logs for scheduler messages
- Verify no exceptions in scheduler

### Issue: Articles Not Generating

**Possible Causes:**
- GEMINI_API_KEY not set or invalid
- Supabase connection issues
- Scheduler not running

**Solutions:**
- Check Railway logs for API errors
- Verify GEMINI_API_KEY is correct
- Check Supabase connection in logs
- Manually trigger: `POST /api/generate-article`

## Testing After Deployment

1. **Health Check**
   ```bash
   curl https://your-app.railway.app/api/health
   ```

2. **Generate Article**
   ```bash
   curl -X POST https://your-app.railway.app/api/generate-article
   ```

3. **Get Articles**
   ```bash
   curl https://your-app.railway.app/api/articles
   ```

4. **Check Logs**
   - Railway Dashboard → Logs
   - Look for article generation messages
   - Check for any errors

## Monitoring

### What to Watch in Logs

**Good Signs:**
- ✅ Supabase connection verified
- ✅ Background scheduler started
- ✅ Article generation started
- ✅ Article saved to Supabase

**Warning Signs:**
- ⚠️ WARNING: Could not verify Supabase connection
- ⚠️ WARNING: No images found
- ⚠️ ERROR: Failed to save article

**Error Signs:**
- ❌ Error initializing Supabase
- ❌ GEMINI_API_KEY missing
- ❌ Table 'articles' does not exist

## Post-Deployment

1. ✅ Verify health endpoint works
2. ✅ Check logs for successful startup
3. ✅ Generate a test article
4. ✅ Verify article appears in Supabase
5. ✅ Check frontend can fetch articles
6. ✅ Monitor scheduler (check logs every 30 min)

## Files That Must Exist

- ✅ `MODEL/Procfile` - Start command
- ✅ `MODEL/requirements.txt` - Dependencies
- ✅ `MODEL/wsgi.py` - WSGI entry point
- ✅ `MODEL/api.py` - Main application
- ✅ `MODEL/model.py` - CrewAI model
- ✅ `MODEL/railway.json` - Railway config (optional but recommended)

## Notes

- Railway automatically sets `PORT` environment variable
- Railway uses ephemeral filesystem (files are lost on restart)
- All data should be stored in Supabase (not local files)
- Background threads (scheduler) work fine on Railway
- Gunicorn workers are configured for Railway's environment

