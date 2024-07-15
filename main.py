from global_vars import SITES
from blog_parser import BlogParser

if __name__ == '__main__':
    for site in SITES:
        parser = BlogParser(site)
        blog_posts = parser.parse()
        for post in blog_posts: 
            print(post)
