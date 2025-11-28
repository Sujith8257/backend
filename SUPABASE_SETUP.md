# Supabase Setup Guide for Flash News AI

This guide will help you set up Supabase for storing articles in your Flash News AI application.

## Step 1: Create a Supabase Project

1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in:
   - **Name**: Flash News AI (or your preferred name)
   - **Database Password**: Choose a strong password (save it!)
   - **Region**: Choose the closest region to your users
5. Click "Create new project" and wait for it to be ready (2-3 minutes)

## Step 2: Run the SQL Schema

1. In your Supabase project dashboard, go to **SQL Editor** (left sidebar)
2. Click **New Query**
3. Copy the entire contents of `supabase_schema.sql`
4. Paste it into the SQL Editor
5. Click **Run** (or press Ctrl+Enter)
6. You should see "Success. No rows returned"

This will create:
- `articles` table with all necessary columns
- Indexes for fast queries
- Row Level Security (RLS) policies
- A view for article summaries

## Step 3: Get Your Supabase Credentials

1. In your Supabase project dashboard, go to **Settings** (gear icon)
2. Click **API** in the left sidebar
3. You'll see:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **API Keys**: 
     - `anon` key (public, for client-side)
     - `service_role` key (secret, for server-side) ⚠️ **Use this one!**

## Step 4: Configure Environment Variables

Add these to your `MODEL/.env` file:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-service-role-key-here
SUPABASE_STORAGE_ENABLED=true
```

**Important Notes:**
- Use the **service_role** key, NOT the anon key (for backend operations)
- Set `SUPABASE_STORAGE_ENABLED=true` to enable Supabase storage
- If set to `false`, the app will use file storage only

## Step 5: Install Dependencies

Make sure you have the Supabase Python client installed:

```bash
pip install supabase
```

Or if using requirements.txt:

```bash
pip install -r requirements.txt
```

## Step 6: Test the Integration

1. Start your Flask server:
   ```bash
   python api.py
   ```

2. You should see:
   - `✅ Supabase client initialized successfully` (if configured correctly)
   - `ℹ️  Supabase storage disabled (using file storage)` (if not configured)

3. Generate a test article:
   ```bash
   curl -X POST http://localhost:5000/api/generate-article
   ```

4. Check Supabase:
   - Go to **Table Editor** in Supabase dashboard
   - Click on `articles` table
   - You should see your article!

## Storage Modes

The application supports two storage modes:

### 1. Supabase Only (Recommended for Production)
- Set `SUPABASE_STORAGE_ENABLED=true`
- Articles are stored in Supabase database
- File storage is still used as backup

### 2. File Storage Only
- Set `SUPABASE_STORAGE_ENABLED=false` or leave unset
- Articles are stored in `MODEL/articles/` folder
- No database required

### 3. Dual Storage (Default when Supabase enabled)
- Articles are saved to both Supabase AND file storage
- Provides redundancy and backup
- File storage acts as fallback if Supabase fails

## Database Schema

The `articles` table has the following structure:

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT (Primary Key) | Unique article identifier (timestamp-based) |
| `title` | TEXT | Article title |
| `content` | TEXT | Main article content |
| `full_text` | TEXT | Complete article text with sources |
| `created_at` | TIMESTAMPTZ | Article creation timestamp |
| `updated_at` | TIMESTAMPTZ | Last update timestamp (auto-updated) |
| `sources` | JSONB | Array of source objects `[{"name": "...", "url": "..."}]` |
| `images` | JSONB | Array of image URLs `["url1", "url2", ...]` |
| `topics` | JSONB | Array of topic keywords `["topic1", "topic2", ...]` |
| `related_articles` | JSONB | Array of related article references |

## Troubleshooting

### "Supabase package not installed"
```bash
pip install supabase
```

### "Error initializing Supabase"
- Check that `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Make sure you're using the **service_role** key, not the anon key
- Verify your Supabase project is active

### "Table 'articles' does not exist"
- Run the SQL schema from `supabase_schema.sql` in the SQL Editor

### "Permission denied" or RLS errors
- Check that RLS policies are created (they're in the SQL schema)
- Verify you're using the service_role key (bypasses RLS)

## Benefits of Supabase Storage

✅ **Scalability**: Handle millions of articles without file system limits  
✅ **Performance**: Fast queries with indexes and full-text search  
✅ **Reliability**: Automatic backups and point-in-time recovery  
✅ **Accessibility**: Query articles via API from anywhere  
✅ **Analytics**: Easy to run queries and generate reports  
✅ **Multi-instance**: Multiple servers can share the same database  

## Next Steps

- Set up Supabase Storage for image uploads (optional)
- Configure backups and retention policies
- Set up monitoring and alerts
- Consider adding user authentication for admin features

