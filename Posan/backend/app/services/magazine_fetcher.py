"""
Monthly Magazine Fetcher Service
Fetches educational content from RSS feeds and web sources,
then creates kid-friendly magazines with articles for the Poshan app.

Updated: Auto-refreshes every month with latest web content.
Sources include National Geographic Kids, NASA, Smithsonian, PBS Kids, and more.
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import re
import calendar
import json
import hashlib
import random

# Educational RSS feeds and web sources for kids
CONTENT_SOURCES = {
    "science": {
        "feeds": [
            "https://www.sciencenewsforstudents.org/feed",
            "https://kids.nationalgeographic.com/feed",
            "https://www.newscientist.com/subject/physics/feed/",
            "https://phys.org/rss-feed/breaking/",
            "https://www.livescience.com/feeds/all",
        ],
        "web_pages": [
            "https://www.natgeokids.com/uk/category/discover/science/",
            "https://kids.nationalgeographic.com/science",
            "https://www.sciencenewsforstudents.org",
            "https://www.funkidslive.com/learn/science/",
            "https://easyscienceforkids.com/",
        ],
        "age_group": "9-11",
        "emoji": "🔬",
    },
    "nature": {
        "feeds": [
            "https://kids.nationalgeographic.com/feed",
            "https://www.worldwildlife.org/blog.xml",
            "https://www.treehugger.com/feeds/all.rss",
        ],
        "web_pages": [
            "https://www.natgeokids.com/uk/category/discover/animals/",
            "https://kids.nationalgeographic.com/animals",
            "https://www.worldwildlife.org/species",
            "https://www.dkfindout.com/us/animals-and-nature/",
        ],
        "age_group": "6-8",
        "emoji": "🌿",
    },
    "space": {
        "feeds": [
            "https://www.nasa.gov/feed/",
            "https://spacenews.com/feed/",
            "https://www.space.com/feeds/all",
        ],
        "web_pages": [
            "https://spaceplace.nasa.gov/menu/play/",
            "https://solarsystem.nasa.gov/news/latest/",
            "https://www.esa.int/kids/",
        ],
        "age_group": "9-11",
        "emoji": "🚀",
    },
    "technology": {
        "feeds": [
            "https://www.wired.com/feed/rss",
            "https://mashable.com/feeds/rss/tech",
        ],
        "web_pages": [
            "https://scratch.mit.edu/explore/projects/all",
            "https://code.org/learn",
            "https://www.tynker.com/blog/",
        ],
        "age_group": "12-14",
        "emoji": "💻",
    },
    "stories": {
        "feeds": [],
        "web_pages": [
            "https://www.storyberries.com",
            "https://www.freechildrenstories.com",
            "https://www.storynory.com/",
            "https://monkeypen.com/pages/free-childrens-books",
        ],
        "age_group": "3-5",
        "emoji": "📖",
    },
    "history": {
        "feeds": [
            "https://www.smithsonianmag.com/rss/latest_articles/",
            "https://www.history.com/rss/news",
        ],
        "web_pages": [
            "https://www.natgeokids.com/uk/category/discover/history/",
            "https://kids.britannica.com/kids/article/history/353212",
            "https://www.dkfindout.com/us/history/",
        ],
        "age_group": "9-11",
        "emoji": "🏛️",
    },
    "health": {
        "feeds": [],
        "web_pages": [
            "https://kidshealth.org/en/kids/",
            "https://www.nourishinteractive.com/nutrition-education-printables",
        ],
        "age_group": "6-8",
        "emoji": "🍎",
    },
    "arts": {
        "feeds": [],
        "web_pages": [
            "https://www.tate.org.uk/kids",
            "https://artsandculture.google.com/category/artist",
        ],
        "age_group": "6-8",
        "emoji": "🎨",
    },
}

# Monthly themes for each month (1-12)
MONTHLY_THEMES = {
    1: {"theme": "New Year & Winter Wonders", "topics": ["winter science", "new year traditions", "arctic animals", "snow"]},
    2: {"theme": "Love & Friendship", "topics": ["kindness", "friendship in nature", "heart science", "valentine traditions"]},
    3: {"theme": "Spring & Growth", "topics": ["plant growth", "spring animals", "weather changes", "gardening for kids"]},
    4: {"theme": "Earth Day & Environment", "topics": ["recycling", "endangered species", "climate for kids", "ocean conservation"]},
    5: {"theme": "Exploration & Adventure", "topics": ["famous explorers", "space missions", "ocean exploration", "mountains"]},
    6: {"theme": "Summer Science", "topics": ["sun and light", "summer insects", "water science", "outdoor experiments"]},
    7: {"theme": "Technology & Innovation", "topics": ["coding for kids", "robots", "inventions", "future technology"]},
    8: {"theme": "World Cultures", "topics": ["world festivals", "foods around the world", "languages", "traditions"]},
    9: {"theme": "Back to School", "topics": ["study tips", "math fun", "reading adventures", "school science"]},
    10: {"theme": "Halloween & Spooky Science", "topics": ["nocturnal animals", "spooky science experiments", "optical illusions", "dinosaurs"]},
    11: {"theme": "Gratitude & Giving", "topics": ["thankfulness", "helping others", "harvest science", "food science"]},
    12: {"theme": "Holidays & Year in Review", "topics": ["holiday traditions worldwide", "winter solstice", "year's best discoveries", "holiday crafts"]},
}

# Rotating cover images per month (Unsplash photo IDs) so each month looks fresh
MONTHLY_COVER_IMAGES = {
    1: {  # January
        "3-5": "1516627145497-ae6968895b74",   # snowy playful scene
        "6-8": "1457269449834-928af64c684d",   # winter adventure
        "9-11": "1483664852095-d6cc6870702d",  # snowflake science
        "12-14": "1518770660439-4636190af475",  # winter tech
    },
    2: {  # February
        "3-5": "1518199266791-5375a83190b7",   # hearts & love
        "6-8": "1529156069898-49953bc6d001",   # friendship
        "9-11": "1559757148-5c2bfa4007dc",     # heart science
        "12-14": "1516321497487-e288fb19713f",  # social media / connection
    },
    3: {  # March
        "3-5": "1490750967868-88aa4f44baee",   # spring flowers
        "6-8": "1462275646964-a0e3c11f18a6",   # garden discovery
        "9-11": "1416879595882-3373a0480b5b",  # plant growth
        "12-14": "1504567961542-e24d9439a724",  # biotech / green
    },
    4: {  # April
        "3-5": "1500530855697-b586d89ba3ee",   # nature / animals
        "6-8": "1441974231531-c6227db76b6e",   # earth / planet
        "9-11": "1446776811953-b23d57bd21aa",  # ocean
        "12-14": "1473448912268-2022ce9509d8",  # sustainability
    },
    5: {  # May
        "3-5": "1503454537195-1dcabb73ffb9",   # colorful kids
        "6-8": "1501349800519-48093d60bde0",   # nature adventure
        "9-11": "1451187580459-43490279c0fa",  # space exploration
        "12-14": "1485827404703-89b55fcc595e",  # tech innovation
    },
    6: {  # June
        "3-5": "1507525428034-b723cf961d3e",   # sunny beach
        "6-8": "1473116763249-2faaef81ccda",   # summer insects
        "9-11": "1507400492013-162706c8c05e",  # sun & light
        "12-14": "1504384308090-c894fdcc538d",  # outdoor science
    },
    7: {  # July
        "3-5": "1535572290543-960a8046f5af",   # playful robots
        "6-8": "1485827404703-89b55fcc595e",   # gadgets
        "9-11": "1518770660439-4636190af475",  # coding
        "12-14": "1550751827-4bd374c3f58b",    # AI / robotics
    },
    8: {  # August
        "3-5": "1533174072545-7a4b6ad7a6c3",   # world cultures
        "6-8": "1504457047772-27faf794c6c8",   # food
        "9-11": "1523906834658-6e24ef2386f9",  # world map
        "12-14": "1488747279002-c8523379faaa",  # global connection
    },
    9: {  # September
        "3-5": "1503676260728-1c00da094a0b",   # school fun
        "6-8": "1497633762265-9d179a990aa6",   # reading
        "9-11": "1509228468518-180dd4864904",  # math / puzzles
        "12-14": "1434030216411-0b793f4b4173",  # study / library
    },
    10: {  # October
        "3-5": "1508361001413-7a9dca21d490",   # pumpkins
        "6-8": "1509557965875-b88c97052f0e",   # spooky fun
        "9-11": "1462331940025-496dfbfc7564",  # nocturnal animals
        "12-14": "1519222970733-f546218fa6d7",  # optical illusions
    },
    11: {  # November
        "3-5": "1506905925346-21bda4d32df4",   # autumn leaves
        "6-8": "1504754524776-8f4f37790ca0",   # harvest
        "9-11": "1498837167922-ddd27525d352",  # food science
        "12-14": "1488521787991-ed7bbaae773f",  # giving
    },
    12: {  # December
        "3-5": "1512389142860-9c449e58a814",   # holiday joy
        "6-8": "1482517967863-00e15c9b44be",   # winter wonderland
        "9-11": "1451187580459-43490279c0fa",  # year in review / space
        "12-14": "1504384764586-bb4cdc1812f0",  # future / year ahead
    },
}


class MagazineFetcher:
    """Fetches and curates educational content from the web for monthly magazines."""

    def __init__(self, ai_generator=None):
        """
        Args:
            ai_generator: Optional ContentGenerator instance for AI-powered content adaptation.
        """
        self.ai_generator = ai_generator
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; PoshanApp/2.0; Educational Kids Magazine Bot)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

    def get_current_month_theme(self) -> Dict[str, Any]:
        """Get the theme and topics for the current month."""
        month = datetime.now().month
        return MONTHLY_THEMES.get(month, MONTHLY_THEMES[1])

    def fetch_rss_articles(self, feed_url: str, max_articles: int = 5) -> List[Dict[str, str]]:
        """Fetch articles from an RSS feed."""
        articles = []
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:max_articles]:
                title = entry.get("title", "").strip()
                summary = entry.get("summary", entry.get("description", "")).strip()
                link = entry.get("link", "")
                published = entry.get("published", entry.get("updated", ""))

                # Clean HTML from summary
                if summary:
                    soup = BeautifulSoup(summary, "html.parser")
                    summary = soup.get_text(separator=" ").strip()

                # Extract Image
                image_url = ""
                if 'media_content' in entry and len(entry.media_content) > 0:
                    image_url = entry.media_content[0].get('url', '')
                elif 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
                    image_url = entry.media_thumbnail[0].get('url', '')
                elif 'links' in entry:
                    for l in entry.links:
                        if l.get('type', '').startswith('image/') or l.get('rel') == 'enclosure':
                            image_url = l.get('href', '')
                            break
                            
                if title and summary:
                    articles.append({
                        "title": title,
                        "summary": summary[:500],
                        "link": link,
                        "source": feed_url,
                        "published": published,
                        "image_url": image_url,
                    })
        except Exception as e:
            print(f"[WARN] Failed to fetch RSS feed {feed_url}: {e}")
        return articles

    def fetch_web_content(self, url: str) -> List[Dict[str, str]]:
        """Fetch article headlines and summaries from a web page."""
        articles = []
        try:
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Strategy 1: Extract article-like content blocks
            for tag in soup.find_all(["article", "div"], class_=re.compile(r"(post|article|card|entry|story|item|block|feature)", re.I)):
                title_el = tag.find(["h1", "h2", "h3", "h4", "a"])
                summary_el = tag.find(["p", "div"], class_=re.compile(r"(excerpt|summary|desc|text|snippet|preview|teaser|body)", re.I))
                if not summary_el:
                    summary_el = tag.find("p")

                title = title_el.get_text(strip=True) if title_el else ""
                summary = summary_el.get_text(strip=True) if summary_el else ""

                image_url = ""
                img_el = tag.find("img")
                if img_el and img_el.get("src"):
                    from urllib.parse import urljoin
                    image_url = urljoin(url, img_el.get("src"))

                if title and len(title) > 5:
                    articles.append({
                        "title": title[:200],
                        "summary": summary[:500] if summary else "",
                        "link": url,
                        "source": url,
                        "image_url": image_url,
                    })

            # Strategy 2: Look for list items with links (common in kid sites)
            if len(articles) < 3:
                for li in soup.find_all("li", class_=re.compile(r"(post|article|item)", re.I)):
                    a_tag = li.find("a")
                    p_tag = li.find("p")
                    if a_tag:
                        title = a_tag.get_text(strip=True)
                        summary = p_tag.get_text(strip=True) if p_tag else ""
                        image_url = ""
                        img_el = li.find("img")
                        if img_el and img_el.get("src"):
                            from urllib.parse import urljoin
                            image_url = urljoin(url, img_el.get("src"))

                        if title and len(title) > 5:
                            articles.append({
                                "title": title[:200],
                                "summary": summary[:500],
                                "link": url,
                                "source": url,
                                "image_url": image_url,
                            })

            # Strategy 3: Fallback - just grab h2/h3 + next p
            if not articles:
                for heading in soup.find_all(["h2", "h3"])[:10]:
                    title = heading.get_text(strip=True)
                    next_p = heading.find_next("p")
                    summary = next_p.get_text(strip=True) if next_p else ""
                    image_url = ""
                    if title and len(title) > 5:
                        articles.append({
                            "title": title[:200],
                            "summary": summary[:500],
                            "link": url,
                            "source": url,
                            "image_url": image_url,
                        })
        except Exception as e:
            print(f"[WARN] Failed to fetch web content from {url}: {e}")
        return articles[:5]

    def gather_raw_content(self, category: str) -> List[Dict[str, str]]:
        """Gather raw content from all sources for a given category."""
        source = CONTENT_SOURCES.get(category)
        if not source:
            return []

        all_articles = []

        # Fetch from RSS feeds
        for feed_url in source.get("feeds", []):
            all_articles.extend(self.fetch_rss_articles(feed_url, max_articles=3))

        # Fetch from web pages
        for web_url in source.get("web_pages", []):
            all_articles.extend(self.fetch_web_content(web_url))

        # Deduplicate by title similarity
        seen_titles = set()
        unique = []
        for article in all_articles:
            title_key = re.sub(r"[^a-z0-9]", "", article["title"].lower())[:30]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique.append(article)

        # Shuffle to add variety each time
        random.shuffle(unique)
        return unique

    def adapt_for_kids(self, raw_article: Dict[str, str], age_group: str, topic: str) -> Dict[str, Any]:
        """Use AI to adapt a raw article into kid-friendly content."""
        if self.ai_generator:
            try:
                prompt = f"""Rewrite this content for kids aged {age_group} in a fun, educational way.
Make it engaging, easy to understand, and include fun facts.
Keep it between 200-400 words.

Original Title: {raw_article['title']}
Original Content: {raw_article['summary']}
Topic: {topic}

Write it as a kid-friendly magazine article with:
- An exciting introduction
- Fun facts highlighted with emojis
- Simple explanations of complex ideas
- A "Did You Know?" section
- A fun activity or question at the end

Article:"""
                content = self.ai_generator._generate_text(prompt, max_tokens=600, use_fallback=False)
                if content and len(content) > 50:
                    image_md = f"![{raw_article['title']}]({raw_article['image_url']})\n\n" if raw_article.get("image_url") else ""
                    return {
                        "title": raw_article["title"],
                        "content": image_md + content,
                        "source_url": raw_article.get("link", ""),
                    }
            except Exception as e:
                print(f"[WARN] AI adaptation failed: {e}")

        # Fallback: use the raw summary with some formatting
        content = self._format_raw_as_article(raw_article, age_group, topic)
        image_md = f"![{raw_article['title']}]({raw_article['image_url']})\n\n" if raw_article.get("image_url") else ""
        return {
            "title": raw_article["title"],
            "content": image_md + content,
            "source_url": raw_article.get("link", ""),
        }

    def _format_raw_as_article(self, raw: Dict[str, str], age_group: str, topic: str) -> str:
        """Format raw content as a basic kid-friendly article (fallback)."""
        title = raw["title"]
        summary = raw.get("summary", "")

        month_name = datetime.now().strftime("%B %Y")

        article = f"""**{title}**

{summary}

---

**Did You Know?**
Every month, we bring you the latest and most exciting news about {topic}! Stay curious and keep exploring the world around you.

**Fun Activity:**
After reading this article, try to find out 3 more interesting facts about {topic}. Share them with your friends or family!

_Source: Curated for Poshan Magazine - {month_name} Edition_
"""
        return article

    def generate_monthly_magazines(self) -> List[Dict[str, Any]]:
        """
        Generate a full set of monthly magazines with articles.
        Returns a list of magazine dicts ready to be inserted into the database.
        """
        now = datetime.now()
        month_name = now.strftime("%B")
        year = now.year
        theme_info = self.get_current_month_theme()
        theme = theme_info["theme"]
        topics = theme_info["topics"]

        print(f"\n{'='*60}")
        print(f"Generating {month_name} {year} Magazines")
        print(f"Theme: {theme}")
        print(f"{'='*60}\n")

        magazines = []

        # Generate one magazine per age group
        age_groups = {
            "3-5": {
                "name": f"Little Explorers - {month_name} {year}",
                "description": f"Fun stories and activities for toddlers! This month's theme: {theme}",
                "categories": ["stories", "nature"],
                "cover_search": "children+learning+colorful",
            },
            "6-8": {
                "name": f"Young Discoverers - {month_name} {year}",
                "description": f"Exciting adventures and discoveries for young readers! Theme: {theme}",
                "categories": ["nature", "science", "health"],
                "cover_search": "kids+adventure+nature",
            },
            "9-11": {
                "name": f"Knowledge Explorers - {month_name} {year}",
                "description": f"Dive deep into science, history, and more! This month: {theme}",
                "categories": ["science", "history", "space"],
                "cover_search": "science+exploration+kids",
            },
            "12-14": {
                "name": f"Teen Innovators - {month_name} {year}",
                "description": f"Technology, coding, and the future! Featured: {theme}",
                "categories": ["technology", "science", "space"],
                "cover_search": "technology+innovation+teens",
            },
        }

        for age_group, config in age_groups.items():
            print(f"\n--- Creating magazine for age group {age_group} ---")
            print(f"Title: {config['name']}")

            articles_data = []
            article_order = 1

            # Fetch content from each category for this age group
            for category in config["categories"]:
                source_info = CONTENT_SOURCES.get(category, {})
                topic = topics[min(article_order - 1, len(topics) - 1)] if topics else category

                print(f"  Fetching {category} content (topic: {topic})...")
                raw_articles = self.gather_raw_content(category)
                print(f"  Found {len(raw_articles)} raw articles")

                # Pick top 1-2 articles per category
                for raw in raw_articles[:2]:
                    adapted = self.adapt_for_kids(raw, age_group, topic)
                    articles_data.append({
                        "title": adapted["title"],
                        "content": adapted["content"],
                        "content_type": "article",
                        "author": f"Poshan {month_name} Team",
                        "reading_time_minutes": max(3, len(adapted["content"].split()) // 150),
                        "age_group": age_group,
                        "order_in_magazine": article_order,
                    })
                    article_order += 1

            # Add a theme-specific article using AI
            if self.ai_generator and topics:
                main_topic = topics[0]
                print(f"  Generating AI article about: {main_topic}...")
                try:
                    ai_article = self.ai_generator.generate_article(
                        topic=main_topic,
                        age_group=age_group,
                        article_type="fun_facts"
                    )
                    articles_data.append({
                        "title": f"{source_info.get('emoji', '📰')} {ai_article['title']}",
                        "content": ai_article["content"],
                        "content_type": "article",
                        "author": "Poshan AI Writer",
                        "reading_time_minutes": max(3, len(ai_article["content"].split()) // 150),
                        "age_group": age_group,
                        "order_in_magazine": article_order,
                    })
                    article_order += 1
                except Exception as e:
                    print(f"  [WARN] AI article generation failed: {e}")

            # Monthly rotating cover image
            cover_url = f"https://images.unsplash.com/photo-{_get_monthly_cover_photo_id(now.month, age_group)}?w=400&h=600&fit=crop"

            magazine = {
                "magazine": {
                    "title": config["name"],
                    "description": config["description"],
                    "age_group": age_group,
                    "issue_number": now.month,
                    "cover_image_url": cover_url,
                    "is_published": True,
                    "publication_date": datetime(year, now.month, 1),
                },
                "articles": articles_data,
            }
            magazines.append(magazine)

            print(f"  Created magazine with {len(articles_data)} articles")

        print(f"\n{'='*60}")
        print(f"Generated {len(magazines)} magazines for {month_name} {year}")
        print(f"{'='*60}\n")

        return magazines

    def generate_fallback_magazines(self) -> List[Dict[str, Any]]:
        """
        Generate magazines with curated fallback content when web fetching fails.
        Ensures magazines are always created even without internet access.
        """
        now = datetime.now()
        month_name = now.strftime("%B")
        year = now.year
        theme_info = self.get_current_month_theme()
        theme = theme_info["theme"]
        topics = theme_info["topics"]

        magazines = []

        fallback_content = {
            "3-5": {
                "title": f"Little Explorers - {month_name} {year}",
                "articles": [
                    {
                        "title": f"A {month_name} Story for Little Ones",
                        "content": f"""Once upon a time, in the month of {month_name}, a little bear named Benny went on an adventure!

Benny was curious about {topics[0] if topics else 'the world'}. He asked his mommy, "Why does the world change every month?"

"Because nature loves surprises!" Mommy Bear said with a smile.

Benny explored the forest and found:
- Beautiful flowers changing colors
- Birds singing new songs
- Fluffy clouds making funny shapes

"Every month is special!" Benny cheered.

**Questions for Little Ones:**
- What is your favorite thing about {month_name}?
- Can you draw what you see outside today?
- What makes YOU curious?

**The End**""",
                    },
                    {
                        "title": f"Let's Learn About {month_name}!",
                        "content": f"""**What happens in {month_name}?**

Did you know that {month_name} is month number {now.month} of the year?

**Fun Facts:**
- There are {calendar.monthrange(year, now.month)[1]} days in {month_name} {year}!
- The season right now is {"winter" if now.month in [12,1,2] else "spring" if now.month in [3,4,5] else "summer" if now.month in [6,7,8] else "autumn"}
- Many animals are {_get_seasonal_activity(now.month)} right now!

**Counting Activity:**
Can you count to {now.month}? That's how many months have passed this year!

1... 2... 3... keep going!

**Color Activity:**
Draw a picture of what {month_name} looks like where you live!""",
                    },
                ],
            },
            "6-8": {
                "title": f"Young Discoverers - {month_name} {year}",
                "articles": [
                    {
                        "title": f"Amazing {topics[0].title() if topics else 'Nature'} Facts!",
                        "content": f"""Get ready for some mind-blowing facts about {topics[0] if topics else 'our amazing world'}!

**Fact #1:** Our planet Earth is about 4.5 billion years old - that's older than any dinosaur!

**Fact #2:** There are more trees on Earth than stars in the Milky Way galaxy. Scientists estimate about 3 trillion trees!

**Fact #3:** A day on Venus is longer than a year on Venus. It takes 243 Earth days to rotate once!

**This Month's Theme: {theme}**

{month_name} is a special time because it's all about {theme.lower()}. Here are some cool things happening this month:

- Scientists around the world are making new discoveries every day
- Nature is always changing and adapting
- There are always new things to learn and explore!

**Did You Know?**
The word "{month_name}" comes from ancient history. Every month's name has a fascinating story behind it!

**Your Challenge:**
Can you find 5 interesting facts about {topics[0] if topics else 'nature'} and share them with your class?""",
                    },
                    {
                        "title": f"Healthy Habits for {month_name}",
                        "content": f"""**Stay Healthy This {month_name}!**

Our bodies are amazing machines that need the right fuel to work properly!

**Top 5 Healthy Habits:**
1. Eat colorful fruits and vegetables every day
2. Drink plenty of water (at least 6-8 glasses!)
3. Get at least 60 minutes of active play
4. Sleep 9-11 hours every night
5. Wash your hands often

**{month_name} Seasonal Foods:**
{"Root vegetables like carrots and sweet potatoes keep you warm!" if now.month in [12,1,2] else "Fresh berries and leafy greens are in season!" if now.month in [3,4,5] else "Watermelon, mangoes, and fresh corn are delicious now!" if now.month in [6,7,8] else "Apples, pumpkins, and squash are harvest favorites!"}

**Fun Experiment:**
Try making a rainbow on your plate - eat foods of every color this week!

_Your body will thank you!_""",
                    },
                ],
            },
            "9-11": {
                "title": f"Knowledge Explorers - {month_name} {year}",
                "articles": [
                    {
                        "title": f"Science Spotlight: {topics[0].title() if topics else 'Amazing Discoveries'}",
                        "content": f"""Welcome to this month's Science Spotlight! Our theme for {month_name} is: **{theme}**

**The Big Question:**
What makes {topics[0] if topics else 'science'} so fascinating? Let's explore!

Every month, scientists around the world publish thousands of new research papers. That means there's ALWAYS something new to discover!

**This Month's Top Stories:**

1. **Climate & Environment**: Scientists continue to study how our planet is changing and what we can do to help protect it.

2. **Space Exploration**: New missions and discoveries are revealing secrets about our universe that we never knew before.

3. **Technology Breakthroughs**: AI and robotics are advancing faster than ever, opening up amazing possibilities for the future.

**Experiment of the Month:**
Try this at home! Create a simple weather station:
- Use a glass of water to measure rainfall
- Observe cloud patterns for a week
- Record temperature changes throughout the day

**Career Spotlight:**
This month, we highlight {_get_career_spotlight(now.month)} - a career where you can make a real difference!

**Think About It:**
How do you think the world will change in the next 10 years? Write down your predictions and check them when you're older!""",
                    },
                ],
            },
            "12-14": {
                "title": f"Teen Innovators - {month_name} {year}",
                "articles": [
                    {
                        "title": f"Tech & Innovation: {topics[0].title() if topics else 'The Future'}",
                        "content": f"""Welcome to Teen Innovators! This month we're diving into: **{theme}**

**The World of Technology in {month_name} {year}:**

Technology never stops evolving, and this month is no exception. Here's what's happening in the world of innovation:

**AI & Machine Learning**
Artificial Intelligence continues to transform how we live, learn, and work. From personalized learning apps to creative tools, AI is becoming a bigger part of our daily lives.

**Coding Corner**
Want to build something cool? Here's a project idea for this month:

```python
# Monthly Fact Generator
import random

facts = [
    "The first computer programmer was Ada Lovelace in the 1840s!",
    "The first website ever created is still online today.",
    "There are approximately 700 programming languages.",
    "The average smartphone has more computing power than NASA had in 1969.",
    "Python is named after Monty Python, not the snake!",
]

print(f"Your {'{month_name}'} Tech Fact:")
print(random.choice(facts))
```

**Innovation Challenge:**
This month, try to identify a problem in your daily life and brainstorm a tech solution for it. The best innovations start with observing real problems!

**Career Path:**
Explore careers in {_get_career_spotlight(now.month)}. The future needs YOUR ideas!

**Resources:**
- Scratch (scratch.mit.edu) - Visual programming
- Replit (replit.com) - Code online for free
- Khan Academy - Free courses on everything""",
                    },
                ],
            },
        }

        for age_group, content in fallback_content.items():
            articles_data = []
            for i, article in enumerate(content["articles"], 1):
                articles_data.append({
                    "title": article["title"],
                    "content": article["content"],
                    "content_type": "article",
                    "author": f"Poshan {month_name} Team",
                    "reading_time_minutes": max(3, len(article["content"].split()) // 150),
                    "age_group": age_group,
                    "order_in_magazine": i,
                })

            cover_url = f"https://images.unsplash.com/photo-{_get_monthly_cover_photo_id(now.month, age_group)}?w=400&h=600&fit=crop"

            magazines.append({
                "magazine": {
                    "title": content["title"],
                    "description": f"{theme} - {month_name} {year} Edition for ages {age_group}",
                    "age_group": age_group,
                    "issue_number": now.month,
                    "cover_image_url": cover_url,
                    "is_published": True,
                    "publication_date": datetime(year, now.month, 1),
                },
                "articles": articles_data,
            })

        return magazines


# --- Helper functions ---

def _get_monthly_cover_photo_id(month: int, age_group: str) -> str:
    """Return a curated Unsplash photo ID that rotates monthly per age group."""
    month_covers = MONTHLY_COVER_IMAGES.get(month)
    if month_covers:
        return month_covers.get(age_group, "1503454537195-1dcabb73ffb9")
    # Fallback to static covers if month not found
    return _get_cover_photo_id(age_group)


def _get_cover_photo_id(age_group: str) -> str:
    """Return a curated Unsplash photo ID based on age group (legacy fallback)."""
    covers = {
        "3-5": "1503454537195-1dcabb73ffb9",   # colorful kids
        "6-8": "1501349800519-48093d60bde0",   # nature adventure
        "9-11": "1451187580459-43490279c0fa",  # science/space
        "12-14": "1485827404703-89b55fcc595e", # technology/robots
    }
    return covers.get(age_group, "1503454537195-1dcabb73ffb9")


def _get_seasonal_activity(month: int) -> str:
    """Return what animals are doing in this season."""
    if month in [12, 1, 2]:
        return "hibernating or staying warm in their cozy homes"
    elif month in [3, 4, 5]:
        return "waking up from winter sleep and having babies"
    elif month in [6, 7, 8]:
        return "playing outside, swimming, and gathering food"
    else:
        return "preparing for winter by storing food and growing thick fur"


def _get_career_spotlight(month: int) -> str:
    """Return a featured career for the month."""
    careers = {
        1: "Environmental Scientist",
        2: "Marine Biologist",
        3: "Botanist (Plant Scientist)",
        4: "Climate Researcher",
        5: "Astronaut",
        6: "Solar Energy Engineer",
        7: "AI Developer",
        8: "Cultural Anthropologist",
        9: "Teacher & Educator",
        10: "Paleontologist (Dinosaur Scientist)",
        11: "Nutritionist & Food Scientist",
        12: "Data Scientist",
    }
    return careers.get(month, "Scientist")
