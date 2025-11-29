-- Migration: Add content_preview column to articles table
-- Run this in your Supabase SQL Editor

-- Add content_preview column if it doesn't exist
ALTER TABLE articles 
ADD COLUMN IF NOT EXISTS content_preview TEXT;

-- Add a comment to document the column
COMMENT ON COLUMN articles.content_preview IS '4-5 line summary/preview of the article content for display in feed';

-- Optional: Update existing articles to have content_preview
-- This will generate previews for existing articles
UPDATE articles 
SET content_preview = LEFT(content, 500)
WHERE content_preview IS NULL OR content_preview = '';

