# Railway Deployment Fixes - Article Generation Issues

## Issues Found and Fixed

### 1. ✅ **Critical Bug: Scheduler Sleep Time (FIXED)**
   - **Problem**: Scheduler was sleeping for 18000 seconds (5 hours) instead of 1800 seconds (30 minutes)
   - **Location**: `api.py` line 523
   - **Fix**: Changed `time.sleep(18000)` to `time.sleep(1800)`
   - **Impact**: Articles will now generate every 30 minutes as intended

### 2. ✅ **Procfile Not Using wsgi.py (FIXED)**
   - **Problem**: Procfile was using `gunicorn api:app` which doesn't start the scheduler in production
   - **Location**: `Procfile`
   - **Fix**: Changed to `gunicorn wsgi:app` to ensure scheduler starts properly
   - **Impact**: Background scheduler will now start automatically in production

### 3. ✅ **Improved Error Handling (FIXED)**
   - **Problem**: Scheduler errors were silently failing without proper logging
   - **Location**: `api.py` scheduler_worker function
   - **Fix**: Added detailed error logging with timestamps and traceback
   - **Impact**: You'll now see detailed error messages in Railway logs if something fails

### 4. ✅ **Initial Article Generation (FIXED)**
   - **Problem**: No article was generated on startup in production
   - **Location**: `wsgi.py`
   - **Fix**: Added automatic initial article generation 5 seconds after startup
   - **Impact**: First article will be generated immediately when the app starts

### 5. ✅ **Supabase Connection Verification (ADDED)**
   - **Problem**: No verification that Supabase is connected on startup
   - **Location**: `wsgi.py`
   - **Fix**: Added connection check that runs before scheduler starts
   - **Impact**: You'll see clear error messages if Supabase credentials are wrong

## What to Check in Railway

### 1. Environment Variables
Make sure these are set in Railway Dashboard → Variables:
```
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key  (NOT anon key!)
PORT=5000  (Railway sets this automatically, but verify)
```

**Important**: Use the **service_role** key for `SUPABASE_KEY`, not the anon key!

### 2. Root Directory
- In Railway Dashboard → Service → Settings
- Set **Root Directory** to: `MODEL`

### 3. Build Settings
- Railway should auto-detect Python from `requirements.txt`
- If issues persist, set Builder to **Nixpacks** in Settings → Build

### 4. Check Logs
After redeploying, check Railway logs for:
- ✅ "Supabase connection verified"
- ✅ "Background scheduler started in production mode"
- ✅ "Generating initial article on startup..."
- ✅ "Article generated and saved to Supabase"

If you see errors:
- ❌ "SUPABASE_URL and SUPABASE_KEY are required" → Set environment variables
- ❌ "Error initializing Supabase" → Check your Supabase credentials
- ❌ "Table 'articles' does not exist" → Run the SQL schema in Supabase

## Testing After Deployment

1. **Check Health Endpoint**: 
   ```
   https://your-railway-app.railway.app/api/health
   ```
   Should return: `{"status": "healthy"}`

2. **Manually Trigger Article Generation**:
   ```
   POST https://your-railway-app.railway.app/api/generate-article
   ```
   This will generate an article immediately and save it to Supabase

3. **Check Articles**:
   ```
   GET https://your-railway-app.railway.app/api/articles
   ```
   Should return a list of articles from Supabase

4. **Monitor Logs**:
   - Watch Railway logs for scheduler messages every 30 minutes
   - Look for "Starting article generation..." messages
   - Check for any error messages

## Files Modified

1. `MODEL/api.py` - Fixed scheduler sleep time and improved error handling
2. `MODEL/Procfile` - Changed to use wsgi.py
3. `MODEL/wsgi.py` - Added initial article generation and Supabase verification

## Next Steps

1. **Commit and push** these changes to your repository
2. **Redeploy** on Railway (should happen automatically if connected to GitHub)
3. **Check Railway logs** to verify everything starts correctly
4. **Wait 5-10 seconds** after deployment for initial article generation
5. **Check Supabase** to verify articles are being saved

## Troubleshooting

If articles still aren't generating:

1. **Check Railway Logs**: Look for error messages
2. **Verify Environment Variables**: Make sure all are set correctly
3. **Test Supabase Connection**: Try manually calling `/api/generate-article`
4. **Check Supabase Table**: Verify the `articles` table exists and has proper permissions
5. **Verify GEMINI_API_KEY**: Make sure it's valid and has quota remaining

## Expected Behavior

After these fixes:
- ✅ Scheduler runs every 30 minutes (not 5 hours)
- ✅ Initial article generates 5 seconds after startup
- ✅ All articles are saved to Supabase
- ✅ Detailed logs show what's happening
- ✅ Errors are caught and logged instead of silently failing

