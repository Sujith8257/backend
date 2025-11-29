# Fix: content_preview Column Error

## Error Message
```
❌ Error saving article to Supabase: {'message': "Could not find the 'content_preview' column of 'articles' in the schema cache", 'code': 'PGRST204', 'hint': None, 'details': None}
```

## Quick Fix

The `content_preview` column doesn't exist in your Supabase database. You need to add it.

### Option 1: Run the Migration SQL (Recommended)

1. Go to your Supabase Dashboard
2. Click on **SQL Editor** (left sidebar)
3. Click **New Query**
4. Copy and paste this SQL:

```sql
ALTER TABLE articles 
ADD COLUMN IF NOT EXISTS content_preview TEXT;
```

5. Click **Run** (or press Ctrl+Enter)
6. You should see: "Success. No rows returned"

### Option 2: Use the Migration File

1. Open `MODEL/add_content_preview_column.sql`
2. Copy the entire contents
3. Paste into Supabase SQL Editor
4. Run it

## What This Does

- Adds the `content_preview` column to your `articles` table
- The column stores a 4-5 line summary of each article
- Used for displaying article previews in the feed

## After Running the Migration

1. The error will stop appearing
2. New articles will have `content_preview` saved
3. Existing articles will get previews generated on-the-fly when loaded

## Temporary Workaround

The code now handles this error gracefully:
- If the column doesn't exist, articles will be saved without `content_preview`
- The app will continue to work
- You'll see a warning message in the logs
- Once you add the column, new articles will include previews

## Verify It Worked

After running the migration, check:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'articles' 
AND column_name = 'content_preview';
```

Should return:
```
content_preview | text
```

