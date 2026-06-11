import feedparser
import urllib.parse

def fetch_news(keyword, max_results=5):
    """
    Function to fetch news from RSS Feed based on keyword.
    Uses Google News endpoint 
    """
    print(f"[INFO] Starting news search for keyword: '{keyword}'...")
    
    # 1. Format keyword for URL
    safe_keyword = urllib.parse.quote(keyword)
    
    # 2. RSS Feed API Endpoint
    rss_url = f"https://news.google.com/rss/search?q={safe_keyword}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        # 3. Execute XML parsing into Python object
        feed = feedparser.parse(rss_url)
        news_list = []
        
        # 4. Validate if no news found
        if not feed.entries:
            print("[WARNING] No news found.")
            return news_list

        # 5. Loop to extract important elements from each news article
        for entry in feed.entries[:max_results]:
            
            # Safety net trick: Capture all possible time tag variations that Google might use
            release_time = entry.get('published') or entry.get('updated') or entry.get('pubDate') or "Unknown release time"
            
            news_item = {
                'title': entry.title,
                'link': entry.link,
                'summary': entry.get('description', ''),
                'date': release_time  # Add captured time result
            }
            news_list.append(news_item)
            
        print(f"[SUCCESS] Successfully fetched {len(news_list)} latest news.")
        return news_list

    except Exception as e:
        print(f"[ERROR] Error occurred while fetching RSS: {e}")
        return []

# LOCAL TESTING BLOCK
# Function will ONLY run if executed directly in terminal

if __name__ == "__main__":
    # Test the function with a sample keyword
    test_keyword = "dollar"
    news_results = fetch_news(test_keyword, max_results=3)
    
    print("\n--- SEARCH RESULTS ---")
    for i, news in enumerate(news_results, 1):
        print(f"{i}. Title: {news['title']}")
        print(f"   Link : {news['link']}")
        print(f"   Date : {news['date']}")
        print(f"   Text : {news['summary'][:100]}...\n")