# Supabase SQL Query for Articles Table

Copy and paste this entire SQL query into your Supabase SQL Editor to create the articles table and all necessary components.

## Quick Setup

1. Go to your Supabase project: https://app.supabase.com
2. Navigate to **SQL Editor** (left sidebar)
3. Click **New Query**
4. Paste the SQL below
5. Click **Run** (or press Ctrl+Enter)

---

## Complete SQL Schema

```sql
-- Supabase SQL Schema for Flash News AI Articles
-- Run this in your Supabase SQL Editor

-- Create articles table
CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    full_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- JSONB columns for arrays and complex data
    sources JSONB DEFAULT '[]'::jsonb,
    images JSONB DEFAULT '[]'::jsonb,
    topics JSONB DEFAULT '[]'::jsonb,
    related_articles JSONB DEFAULT '[]'::jsonb,
    
    -- Indexes for better query performance
    CONSTRAINT articles_id_check CHECK (char_length(id) > 0)
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_title ON articles USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_articles_topics ON articles USING gin(topics);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to update updated_at on row update
CREATE TRIGGER update_articles_updated_at 
    BEFORE UPDATE ON articles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) - optional, adjust as needed
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- Create policy to allow public read access (adjust based on your needs)
CREATE POLICY "Allow public read access" ON articles
    FOR SELECT
    USING (true);

-- Create policy to allow service role insert/update (for your backend)
-- Note: This requires service_role key, not anon key
CREATE POLICY "Allow service role insert" ON articles
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Allow service role update" ON articles
    FOR UPDATE
    USING (true);

-- Optional: Create a view for article summaries (without full_text for list views)
CREATE OR REPLACE VIEW article_summaries AS
SELECT 
    id,
    title,
    LEFT(content, 500) as content_preview,
    created_at,
    sources,
    images,
    topics,
    related_articles
FROM articles
ORDER BY created_at DESC;

-- Grant permissions (adjust based on your setup)
-- GRANT SELECT ON articles TO anon;
-- GRANT SELECT ON article_summaries TO anon;
```

---

## What This Creates

### 1. **articles Table**
   - `id` (TEXT, Primary Key): Unique article identifier
   - `title` (TEXT): Article title
   - `content` (TEXT): Main article content
   - `full_text` (TEXT): Complete article with sources
   - `created_at` (TIMESTAMPTZ): Creation timestamp
   - `updated_at` (TIMESTAMPTZ): Last update timestamp (auto-updated)
   - `sources` (JSONB): Array of source objects
   - `images` (JSONB): Array of image URLs
   - `topics` (JSONB): Array of topic keywords
   - `related_articles` (JSONB): Array of related article references

### 2. **Indexes**
   - `idx_articles_created_at`: Fast sorting by date
   - `idx_articles_title`: Full-text search on titles
   - `idx_articles_topics`: Fast topic-based queries

### 3. **Triggers**
   - Auto-updates `updated_at` when an article is modified

### 4. **Row Level Security (RLS)**
   - Public read access (anyone can read articles)
   - Service role can insert/update (your backend)

### 5. **Views**
   - `article_summaries`: Lightweight view for listing articles (excludes full_text)

---

## Verification

After running the SQL, verify the table was created:

1. Go to **Table Editor** in Supabase dashboard
2. You should see the `articles` table
3. Click on it to view the structure

---

## Example Queries

### Get all articles (newest first)
```sql
SELECT * FROM articles ORDER BY created_at DESC;
```

### Get article by ID
```sql
SELECT * FROM articles WHERE id = '20251129024626';
```

### Search articles by title
```sql
SELECT * FROM articles 
WHERE to_tsvector('english', title) @@ to_tsquery('english', 'trump');
```

### Get articles with specific topic
```sql
SELECT * FROM articles 
WHERE topics @> '["politics"]'::jsonb;
```

### Get article summaries (without full_text)
```sql
SELECT * FROM article_summaries LIMIT 10;
```

---

## Troubleshooting

### "relation 'articles' already exists"
- The table already exists. You can either:
  - Drop it first: `DROP TABLE articles CASCADE;`
  - Or use `CREATE TABLE IF NOT EXISTS` (already in the query)

### "permission denied"
- Make sure you're using the **service_role** key in your backend
- Check that RLS policies are created correctly

### "column does not exist"
- Make sure you ran the complete SQL schema
- Check the table structure in Table Editor

---

## Next Steps

1. Configure your `.env` file with Supabase credentials
2. Set `SUPABASE_STORAGE_ENABLED=true` in your `.env`
3. Restart your Flask server
4. Generate a test article to verify it saves to Supabase

For detailed setup instructions, see `SUPABASE_SETUP.md`.

