# Railway Deployment Fix

## Problem
Railway is trying to use `mise` to install Python, which is failing with:
```
mise ERROR no precompiled python found for core:python@3.11.0
```

## Solution

### Option 1: Use Railway's Auto-Detection (Recommended)

1. **Delete or rename `runtime.txt`** - Railway will auto-detect Python from `requirements.txt`
2. **Make sure `railway.json` exists** in the MODEL folder (already created)
3. **Set Python version in Railway Dashboard:**
   - Go to your Railway project
   - Settings → Variables
   - Add: `PYTHON_VERSION=3.11.6`

### Option 2: Use Nixpacks Explicitly

1. In Railway Dashboard:
   - Go to your service
   - Settings → Build
   - Set Builder to: **Nixpacks**
   - Railway will use the `railway.json` configuration

### Option 3: Remove runtime.txt

If Railway keeps trying to use mise:

1. **Delete `MODEL/runtime.txt`** (or rename it)
2. Railway will auto-detect Python 3.11 from your code
3. Or specify in Railway dashboard settings

## Steps to Fix:

1. **In Railway Dashboard:**
   - Go to your project → Service → Settings
   - Under "Build" section:
     - Set Builder: **Nixpacks** (not mise)
     - Or remove any mise-related settings

2. **Environment Variables:**
   Make sure these are set in Railway:
   ```
   GEMINI_API_KEY=your_key
   SUPABASE_URL=your_url
   SUPABASE_KEY=your_key
   PORT=5000 (Railway sets this automatically)
   ```

3. **Root Directory:**
   - In Railway service settings
   - Set Root Directory to: `MODEL`

4. **Redeploy:**
   - Push your changes to GitHub
   - Railway will automatically redeploy
   - Or manually trigger a redeploy

## Alternative: Use Python Buildpack

If Nixpacks doesn't work:

1. In Railway Dashboard → Service → Settings
2. Under "Build" → Builder
3. Select: **Python Buildpack**
4. It will use `requirements.txt` and `Procfile`

## Files Created:

- ✅ `railway.json` - Railway configuration
- ✅ `.python-version` - Python version specification
- ✅ Updated `runtime.txt` - Python version (if needed)
- ✅ Updated `Procfile` - Removed release command
- ✅ Updated `wsgi.py` - Removed file storage references

## Verification:

After deployment, check Railway logs:
- Should see: "Background scheduler started in production mode"
- Should see: "✅ Supabase client initialized successfully"
- Should NOT see any mise errors

