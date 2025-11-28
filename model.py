import os
import requests
import json
import feedparser
from datetime import datetime
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise EnvironmentError(
        "GEMINI_API_KEY missing. Add it to a .env file or the environment."
    )

# Get model from environment or use default (gemini-2.0-flash-lite has better free tier limits: 30 RPM, 1M TPM)
# You can override by setting GEMINI_MODEL in .env file
gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")

shared_llm = LLM(
    model=gemini_model,  # Default: gemini-2.0-flash-lite (30 RPM, 1M TPM free tier)
    api_key=gemini_api_key,
    temperature=0.7,
    timeout=120,
    max_tokens=4000,
    top_p=0.9,
    frequency_penalty=0.1,
    presence_penalty=0.1,
)

# News API functions
def fetch_newsapi():
    """Fetch news from NewsAPI"""
    try:
        url = "https://newsapi.org/v2/top-headlines?country=in&apiKey=2af46c8507fe47e18b7b2fcd5ef74dce"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('articles', [])
    except Exception as e:
        print(f"NewsAPI error: {e}")
    return []

def fetch_newsdata():
    """Fetch news from NewsData.io"""
    try:
        url = "https://newsdata.io/api/1/news?apikey=pub_c894654a54c547af95e9f015b256dd28&q=technology"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
    except Exception as e:
        print(f"NewsData.io error: {e}")
    return []

def fetch_gdelt(query="world"):
    """Fetch news from GDELT"""
    try:
        url = f"https://api.gdeltproject.org/api/v2/doc/doc?query={query}&mode=ArtList&format=json&maxrecords=50"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('articles', [])
    except Exception as e:
        print(f"GDELT error: {e}")
    return []

def fetch_rss_feed(url):
    """Fetch news from RSS feed"""
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:20]:  # Limit to 20 entries
            # Extract image from media:content or enclosure
            image_url = ''
            if hasattr(entry, 'media_content'):
                for media in entry.media_content:
                    if media.get('type', '').startswith('image/'):
                        image_url = media.get('url', '')
                        break
            if not image_url and hasattr(entry, 'enclosures'):
                for enclosure in entry.enclosures:
                    if enclosure.get('type', '').startswith('image/'):
                        image_url = enclosure.get('href', '')
                        break
            # Also check for media:thumbnail
            if not image_url and hasattr(entry, 'media_thumbnail'):
                for thumb in entry.media_thumbnail:
                    image_url = thumb.get('url', '')
                    break
            
            articles.append({
                'title': entry.get('title', ''),
                'description': entry.get('description', ''),
                'link': entry.get('link', ''),
                'published': entry.get('published', ''),
                'source': feed.feed.get('title', 'RSS Feed'),
                'image_url': image_url
            })
        return articles
    except Exception as e:
        print(f"RSS feed error ({url}): {e}")
    return []

def fetch_google_news_rss():
    """Fetch from Google News RSS"""
    return fetch_rss_feed("https://news.google.com/rss")

def fetch_bbc_rss():
    """Fetch from BBC RSS"""
    return fetch_rss_feed("https://feeds.bbci.co.uk/news/rss.xml")

def fetch_reddit_news():
    """Fetch top posts from Reddit news subreddits"""
    try:
        subreddits = ['news', 'worldnews', 'technology']
        articles = []
        for subreddit in subreddits:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for post in data.get('data', {}).get('children', []):
                    post_data = post.get('data', {})
                    # Extract image URL from Reddit post
                    image_url = ''
                    # Check preview images
                    if 'preview' in post_data and 'images' in post_data['preview']:
                        if post_data['preview']['images']:
                            image_url = post_data['preview']['images'][0].get('source', {}).get('url', '')
                            # Reddit URLs are escaped, unescape them
                            if image_url:
                                image_url = image_url.replace('&amp;', '&')
                    # Check thumbnail
                    if not image_url:
                        thumbnail = post_data.get('thumbnail', '')
                        if thumbnail and thumbnail not in ['self', 'default', 'nsfw']:
                            image_url = thumbnail
                    # Check URL if it's a direct image link
                    url_link = post_data.get('url', '')
                    if not image_url and url_link:
                        if any(ext in url_link.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                            image_url = url_link
                    
                    articles.append({
                        'title': post_data.get('title', ''),
                        'description': post_data.get('selftext', ''),
                        'link': f"https://reddit.com{post_data.get('permalink', '')}",
                        'published': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                        'source': f"Reddit r/{subreddit}",
                        'score': post_data.get('score', 0),
                        'image_url': image_url
                    })
    except Exception as e:
        print(f"Reddit error: {e}")
    return articles

def aggregate_all_news():
    """Fetch from all news sources and aggregate"""
    all_articles = []
    
    # Fetch from APIs
    newsapi_articles = fetch_newsapi()
    newsdata_articles = fetch_newsdata()
    gdelt_articles = fetch_gdelt("world")
    google_news = fetch_google_news_rss()
    bbc_news = fetch_bbc_rss()
    reddit_news = fetch_reddit_news()
    
    # Normalize and add source info
    for article in newsapi_articles:
        article['source_name'] = article.get('source', {}).get('name', 'NewsAPI')
        article['image_url'] = article.get('urlToImage', '')
        all_articles.append(article)
    
    for article in newsdata_articles:
        article['source_name'] = article.get('source_id', 'NewsData.io')
        article['image_url'] = article.get('image_url', '')
        all_articles.append(article)
    
    for article in gdelt_articles:
        article['source_name'] = article.get('source', 'GDELT')
        article['image_url'] = article.get('image', '')
        all_articles.append(article)
    
    for article in google_news:
        article['source_name'] = 'Google News'
        if 'image_url' not in article:
            article['image_url'] = ''
        all_articles.append(article)
    
    for article in bbc_news:
        article['source_name'] = 'BBC'
        if 'image_url' not in article:
            article['image_url'] = ''
        all_articles.append(article)
    
    for article in reddit_news:
        article['source_name'] = article.get('source', 'Reddit')
        if 'image_url' not in article:
            article['image_url'] = ''
        all_articles.append(article)
    
    return all_articles

# Create CrewAI tools using BaseTool
class FetchAllNewsSourcesTool(BaseTool):
    name: str = "fetch_all_news_sources"
    description: str = "Fetch real-time news from all available sources: NewsAPI, NewsData.io, GDELT, Google News RSS, BBC RSS, and Reddit. Returns aggregated news articles with full content and image URLs. IMPORTANT: Extract and include image_url field from each article."
    
    def _run(self) -> str:
        result = aggregate_all_news()
        # Ensure image URLs are prominently included in the output
        formatted_result = []
        for article in result:
            formatted_article = {
                "title": article.get('title', ''),
                "description": article.get('description', ''),
                "content": article.get('content', ''),
                "url": article.get('url', ''),
                "image_url": article.get('image_url', '') or article.get('urlToImage', '') or article.get('image', ''),
                "source_name": article.get('source_name', ''),
                "published": article.get('published', '') or article.get('publishedAt', ''),
            }
            formatted_result.append(formatted_article)
        return json.dumps(formatted_result, indent=2, default=str)

class FetchNewsAPITool(BaseTool):
    name: str = "fetch_newsapi_articles"
    description: str = "Fetch top headlines from NewsAPI for India. Returns articles with image URLs in urlToImage field."
    
    def _run(self) -> str:
        result = fetch_newsapi()
        # Format to highlight image URLs
        formatted = []
        for article in result:
            formatted.append({
                "title": article.get('title', ''),
                "description": article.get('description', ''),
                "url": article.get('url', ''),
                "image_url": article.get('urlToImage', ''),
                "source": article.get('source', {}).get('name', ''),
                "publishedAt": article.get('publishedAt', '')
            })
        return json.dumps(formatted, indent=2, default=str)

class FetchNewsDataTool(BaseTool):
    name: str = "fetch_newsdata_articles"
    description: str = "Fetch technology news from NewsData.io. Returns articles with image URLs in image_url field."
    
    def _run(self) -> str:
        result = fetch_newsdata()
        # Format to highlight image URLs
        formatted = []
        for article in result:
            formatted.append({
                "title": article.get('title', ''),
                "description": article.get('description', ''),
                "url": article.get('link', ''),
                "image_url": article.get('image_url', ''),
                "source": article.get('source_id', ''),
                "pubDate": article.get('pubDate', '')
            })
        return json.dumps(formatted, indent=2, default=str)

class FetchGDELTTool(BaseTool):
    name: str = "fetch_gdelt_articles"
    description: str = "Fetch global events from GDELT API. Provide a query term to search for specific topics. Returns articles with image URLs in image field. Call with: fetch_gdelt_articles(query='your_search_term')"
    
    def _run(self, query: str = "world") -> str:
        result = fetch_gdelt(query)
        # Format to highlight image URLs
        formatted = []
        for article in result:
            formatted.append({
                "title": article.get('title', ''),
                "url": article.get('url', ''),
                "image_url": article.get('image', ''),
                "source": article.get('source', ''),
                "published": article.get('seendate', '')
            })
        return json.dumps(formatted, indent=2, default=str)

class FetchRSSFeedsTool(BaseTool):
    name: str = "fetch_rss_feeds"
    description: str = "Fetch news from Google News RSS and BBC RSS feeds. Returns articles with image URLs extracted from media content."
    
    def _run(self) -> str:
        google = fetch_google_news_rss()
        bbc = fetch_bbc_rss()
        # Format to highlight image URLs
        formatted_google = [{
            "title": a.get('title', ''),
            "description": a.get('description', ''),
            "url": a.get('link', ''),
            "image_url": a.get('image_url', ''),
            "published": a.get('published', '')
        } for a in google]
        formatted_bbc = [{
            "title": a.get('title', ''),
            "description": a.get('description', ''),
            "url": a.get('link', ''),
            "image_url": a.get('image_url', ''),
            "published": a.get('published', '')
        } for a in bbc]
        result = {"google_news": formatted_google, "bbc_news": formatted_bbc}
        return json.dumps(result, indent=2, default=str)

class FetchRedditNewsTool(BaseTool):
    name: str = "fetch_reddit_news"
    description: str = "Fetch top posts from Reddit subreddits: r/news, r/worldnews, r/technology. Returns posts with image URLs from previews or direct image links."
    
    def _run(self) -> str:
        result = fetch_reddit_news()
        # Format to highlight image URLs
        formatted = [{
            "title": a.get('title', ''),
            "description": a.get('description', ''),
            "url": a.get('link', ''),
            "image_url": a.get('image_url', ''),
            "source": a.get('source', ''),
            "score": a.get('score', 0)
        } for a in result]
        return json.dumps(formatted, indent=2, default=str)

# Instantiate tools
fetch_all_news_sources_tool = FetchAllNewsSourcesTool()
fetch_newsapi_tool = FetchNewsAPITool()
fetch_newsdata_tool = FetchNewsDataTool()
fetch_gdelt_tool = FetchGDELTTool()
fetch_rss_feeds_tool = FetchRSSFeedsTool()
fetch_reddit_news_tool = FetchRedditNewsTool()

# Define three agents with distinct responsibilities
news_researcher = Agent(
    role="Global Events Research Analyst",
    goal="Gather the most significant recent events around the world and rank them by their global importance and impact. Then select the top five events and research each thoroughly using trusted international news sources. Include only original images related to the events from credible sources (no AI-generated images).",
    backstory="You are a professional, precise global news analyst with deep expertise in current affairs. You systematically identify and evaluate worldwide events by their significance and impact, then compile detailed, authoritative reports on the top stories. You source all information and images from reliable international outlets, ensuring included images are original and relevant. Your tone is expert, objective, and well-informed.",
    llm=shared_llm,
    tools=[
        fetch_all_news_sources_tool,
        fetch_newsapi_tool,
        fetch_newsdata_tool,
        fetch_gdelt_tool,
        fetch_rss_feeds_tool,
        fetch_reddit_news_tool
    ],
    verbose=True
)

fact_checker = Agent(
    role="Fact Checker",
    goal="Verify accuracy of claims and flag inconsistencies",
    backstory="Thorough reviewer who cross-checks every statement.",
    llm=shared_llm,
)

copywriter = Agent(
    role="Copywriter",
    goal="Produce a comprehensive Flash News article in a lively, engaging tone with proper formatting including sources at the bottom",
    backstory="Seasoned writer specializing in concise news summaries and engaging articles. You excel at creating well-structured articles that inform and captivate readers while maintaining journalistic integrity.",
    llm=shared_llm,
)

# Tasks each agent should perform
research_task = Task(
    description="""
    Use the available tools to fetch real-time news from all available sources:
    - fetch_all_news_sources_tool: Get aggregated news from all sources
    - fetch_newsapi_tool: NewsAPI top headlines
    - fetch_newsdata_tool: NewsData.io technology news
    - fetch_gdelt_tool: GDELT global events (can specify query)
    - fetch_rss_feeds_tool: Google News and BBC RSS feeds
    - fetch_reddit_news_tool: Reddit news from r/news, r/worldnews, r/technology
    
    After collecting all news articles from these sources, rate each event according to:
    1. Global importance (scale 1-10)
    2. Impact level (scale 1-10)
    3. Timeliness/relevance
    
    Select the top 5 events based on combined importance and impact scores.
    
    CRITICAL: For each of the top 5 events, collect and pass COMPLETE information:
    - Full article text/content (DO NOT SUMMARIZE - include the entire article content)
    - Complete descriptions and details
    - Source URLs (multiple sources per event for verification)
    - Original images from the news sources (image URLs from articles, NOT AI-generated)
      * Extract image URLs from the news data (urlToImage, image_url, image fields)
      * CRITICAL: You MUST include at least ONE image URL for each of the top 5 events
      * Include images in the output with clear labels like "Image: [URL]" or "Images: [URL1, URL2]"
      * Only include original news images, never AI-generated images
      * If an event has no image in the source data, try to find a related image from other sources covering the same event
    - Publication dates and timestamps
    - Author information if available
    - Source names and credibility indicators
    - All relevant metadata
    
    IMPORTANT: Do NOT summarize or condense the information. Pass the full, complete details 
    to the next agent so they can perform thorough fact-checking with all available context.
    
    Format the output as a detailed JSON structure with all collected information for each event.
    """,
    expected_output="""
    A comprehensive JSON structure containing the top 5 global events with complete information:
    {
        "events": [
            {
                "title": "Event title",
                "importance_rating": 1-10,
                "impact_rating": 1-10,
                "combined_score": calculated value,
                "full_content": "Complete article text - NOT summarized",
                "description": "Full description - NOT summarized",
                "source_urls": ["url1", "url2", ...],
                "image_urls": ["original_image_url1", "original_image_url2", ...],
                "publication_dates": ["date1", "date2", ...],
                "authors": ["author1", ...],
                "source_names": ["source1", "source2", ...],
                "metadata": {all relevant information}
            },
            ... (4 more events)
        ]
    }
    All content must be complete and unsummarized for the fact-checker agent.
    """,
    agent=news_researcher
)

validate_task = Task(
    description="""
    Receive the complete, unsummarized event information from the research analyst.
    For each of the top 5 events, perform thorough fact-checking:
    - Verify claims against multiple sources
    - Cross-reference information across different news outlets
    - Check for consistency in reporting
    - Identify any discrepancies or uncertainties
    - Verify image authenticity (ensure they are original news images, not AI-generated)
    - Validate publication dates and source credibility
    
    Mark each event with a verification status and provide detailed notes.
    """,
    expected_output="""
    A verification report in JSON format:
    {
        "verification_results": [
            {
                "event_title": "Title",
                "status": "VERIFIED" or "FLAGGED" or "PARTIALLY_VERIFIED",
                "confidence_score": 0-100,
                "source_agreement": "high/medium/low",
                "discrepancies": ["list of any inconsistencies"],
                "image_verification": "verified_original" or "needs_review",
                "notes": "Detailed verification notes",
                "recommended_action": "proceed" or "review" or "exclude"
            },
            ... (for all 5 events)
        ]
    }
    """,
    agent=fact_checker
)

write_task = Task(
    description="""
    Using the verified event information from the fact-checker, create a comprehensive Flash News article.
    
    CRITICAL: The article MUST start with a clear, engaging headline/title on the FIRST LINE.
    The title should:
    - Be 10-100 characters long
    - Capture the essence of the top 5 global events being covered
    - Be informative, attention-grabbing, and newsworthy
    - NOT end with a period, exclamation mark, or question mark
    - Be on its own line at the very beginning, before any article content
    
    The article should:
    1. Start with an engaging headline/title on the first line
    2. Be written in a lively, energetic tone
    3. Cover all verified events in a cohesive narrative
    4. Be well-structured with clear paragraphs
    5. Include relevant details and context
    6. Be comprehensive (500-1500 words)
    
    CRITICAL REQUIREMENT - IMAGES:
    You MUST include at least ONE image URL in the Images section. 
    - Extract image URLs from the news sources provided by the researcher
    - Include at least 1-3 relevant images from the original news articles
    - Images should be from credible news sources (BBC, Reuters, CNN, etc.)
    - DO NOT create fake or placeholder image URLs
    - If you cannot find images, use image URLs from the source articles provided
    
    CRITICAL FORMATTING REQUIREMENT:
    Format the article as follows:
    
    [Title/Headline on first line - 10-100 characters, no punctuation at end]
    
    [Article content here - multiple paragraphs]
    
    Images:
    Image: https://example.com/image1.jpg
    Image: https://example.com/image2.jpg
    (MUST include at least one image URL)
    
    Sources:
    Source: BBC News - https://www.bbc.com/news/article1
    Source: Reuters - https://www.reuters.com/article2
    Source: The Guardian - https://www.theguardian.com/article3
    
    Example:
    Global Markets Surge as Tech Giants Announce Breakthrough AI Developments
    
    In a stunning turn of events, major technology companies have unveiled...
    [rest of article content]
    
    Images:
    Image: https://example.com/image1.jpg
    
    Sources:
    Source: BBC News - https://www.bbc.com/news/article1
    """,
    expected_output="""
    A well-formatted Flash News article with:
    - Clear, engaging headline/title on the FIRST LINE (10-100 characters, no ending punctuation)
    - Comprehensive article content (500-1500 words)
    - Lively, energetic writing style
    - Proper paragraph structure
    - Images section with AT LEAST ONE image URL from news sources (REQUIRED - must include at least 1 image)
    - Sources section at the bottom with source names and URLs
    Format: Title on first line, then content, then "Image: [URL]" for images (minimum 1 image required) and "Source: [Name] - [URL]" for sources
    """,
    agent=copywriter,
    async_execution=False  # ensure it runs after validation completes
)

# Assemble the crew and execute
crew = Crew(
    agents=[news_researcher, fact_checker, copywriter],
    tasks=[research_task, validate_task, write_task],
)

# Only run if executed directly (not when imported)
if __name__ == "__main__":
    result = crew.kickoff()
    print(result)
    
    # Save result to file for API access
    try:
        article_text = str(result)
        sources = []
        
        # Extract sources if present
        if "Sources:" in article_text:
            sources_section = article_text.split("Sources:")[-1]
            for line in sources_section.split('\n'):
                line = line.strip()
                if line and ('http' in line or 'www.' in line):
                    if ' - ' in line:
                        parts = line.split(' - ', 1)
                        source_name = parts[0].replace('Source:', '').strip()
                        source_url = parts[1].strip()
                        sources.append({"name": source_name, "url": source_url})
        
        # Extract title
        title = "Flash News: Top Global Events"
        if '\n' in article_text:
            first_line = article_text.split('\n')[0]
            if len(first_line) < 100 and first_line.strip():
                title = first_line.strip()
        
        # Extract content
        content = article_text
        if "Sources:" in content:
            content = content.split("Sources:")[0].strip()
        
        article_data = {
            "title": title,
            "content": content,
            "sources": sources,
            "full_text": article_text
        }
        
        with open('latest_article.json', 'w', encoding='utf-8') as f:
            json.dump(article_data, f, indent=2, ensure_ascii=False)
        
        print("\nArticle saved to latest_article.json")
    except Exception as e:
        print(f"Error saving article: {e}")
