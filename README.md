# Flash News AI Backend

This directory contains the backend API and AI model for generating Flash News articles.

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the MODEL directory with your API key:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

## Running the API Server

Start the Flask API server:
```bash
python api.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### GET `/api/articles`
Get all articles (newest first). Returns a list of all stored articles with timestamps.

### GET `/api/article/<id>`
Get a specific article by ID.

### GET `/api/article`
Get the latest generated article.

### POST `/api/generate-article`
Manually trigger article generation. This may take a few minutes as it:
1. Fetches news from multiple sources
2. Rates events by importance and impact
3. Fact-checks the information
4. Writes a comprehensive article with sources

### GET `/api/health`
Health check endpoint.

## Automatic Article Generation

When the server starts, it will:
1. Generate the first article immediately
2. Then automatically generate a new article every 30 minutes
3. Store articles in the `articles/` folder
4. Keep only the latest 50 articles (older ones are automatically deleted)

## Article Storage

Articles are automatically stored in the `articles/` folder as individual JSON files. Each article is saved with:
- Unique ID (timestamp-based)
- Title, content, and sources
- Creation timestamp

The system automatically keeps the latest 50 articles and removes older ones.

## Running the Model Directly

You can also run the model directly without the API:
```bash
python model.py
```

This will generate an article and save it to the `articles/` folder.

