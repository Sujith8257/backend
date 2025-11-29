-- Supabase SQL Schema for Flash News AI Articles
-- Run this in your Supabase SQL Editor

-- Create articles table
CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_preview TEXT,  -- 4-5 line summary for preview in feed
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

