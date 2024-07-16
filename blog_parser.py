import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from global_vars import PATH_KEYWORDS


class BlogParser:
    def __init__(self, main_page_url):
        self.main_page_url = main_page_url
        self.html_content = self.fetch_content(self.main_page_url)
        self.soup = BeautifulSoup(self.html_content, 'html.parser')

    def fetch_content(self, url):
        print(f"Fetching content from: {url}")
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    def get_blog_post_links(self):
        links = []
        # Look for <a> tags within common containers
        for container in self.soup.find_all(['article', 'div', 'section']):
            for a_tag in container.find_all('a', href=True):
                href = a_tag['href']
                if any(keyword in href for keyword in PATH_KEYWORDS):
                    full_url = urljoin(self.main_page_url, href)
                    links.append(full_url)
        print(f"Found {len(links)} blog post links")
        return list(set(links))  # Remove duplicates

    def get_title(self, soup):
        title_tag = soup.find('title')
        return title_tag.text.strip() if title_tag else 'No data'

    def get_author(self, soup):
        author = soup.find(attrs={"name": re.compile(r'author', re.I)})
        return author['content'] if author else 'No data'

   
    def get_date(self, soup):
        # Search for common meta tags
        date_meta = soup.find('meta', attrs={"name": re.compile(r'date', re.I)})
        if date_meta and date_meta.has_attr('content'):
            return date_meta['content']
        
        # Search for common itemprop attributes
        date_itemprop = soup.find(attrs={"itemprop": "datePublished"})
        if date_itemprop:
            return date_itemprop['content'] if date_itemprop.has_attr('content') else date_itemprop.text.strip()
        
        # Search for common datetime attributes
        date_time = soup.find('time')
        if date_time and date_time.has_attr('datetime'):
            return date_time['datetime']
        elif date_time:
            return date_time.text.strip()
        
        # Search for common class or ID names
        date_classes_ids = ['date', 'entry-date', 'published', 'post-date', 'article-date', 'time']
        for cls in date_classes_ids:
            date_tag = soup.find(attrs={"class": re.compile(cls, re.I)}) or soup.find(attrs={"id": re.compile(cls, re.I)})
            if date_tag:
                date_text = date_tag.text.strip()
                if re.search(r'\b(?:20\d{2})\b', date_text):  # Ensure the text contains a year (e.g., 2022)
                    return date_text
        
        # Search for specific format "Cutis. 2016 May;97(5):326-329"
        specific_format_match = re.search(r'(\d{4})\s+(\w{3,})', soup.get_text())
        if specific_format_match:
            year = specific_format_match.group(1)
            month = specific_format_match.group(2)
            return f"{month} {year}"
        
        # Search for date in common tags directly, excluding generic text like "© 2024 All rights reserved"
        for tag in ['span', 'div', 'p']:
            date_tag = soup.find(tag, text=re.compile(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|20\d{2}|[01]?\d/[0-3]?\d/[12]\d{3})\b', re.I))
            if date_tag:
                date_text = date_tag.text.strip()
                if not re.search(r'\b(?:©|rights reserved)\b', date_text, re.I):  # Exclude generic copyright statements
                    return date_text
        
        return 'No date found'

    def get_content(self, soup):
        content_tags = ['article', 'div', 'section']
        for tag in content_tags:
            content = soup.find(tag, attrs={"class": re.compile(r'content|post|entry', re.I)})
            if content:
                return content.text.strip()
        return 'No content found'

    def parse_blog_post(self, url):
        html_content = self.fetch_content(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        return {
            'title': self.get_title(soup),
            'author': self.get_author(soup),
            'date': self.get_date(soup),
            'content': self.get_content(soup),
            'url': url
        }

    def parse(self):
        blog_posts = []
        links = self.get_blog_post_links()
        print('len(links)', len(links))
        for link in links:
            print(f"Parsing blog post: {link}")
            try:
                post_data = self.parse_blog_post(link)
                blog_posts.append(post_data)
            except Exception as e:
                print(f"Failed to parse {link}: {e}")
        return blog_posts