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
        date = soup.find(attrs={"name": re.compile(r'date', re.I)})
        return date['content'] if date else 'No data'

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