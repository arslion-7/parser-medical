from global_vars import SITES
from blog_parser import BlogParser
from db_managers.sqlite_manager import DatabaseManager

if __name__ == '__main__':
    db = DatabaseManager("db.sqlite3") # its in .gitignore
    db.create_table()

    for site in SITES:
        parser = BlogParser(site)
        blog_posts = parser.parse()
        for post in blog_posts:
            url = post['url']
            title = post['title']
            print('parsed title', title)
            content = post['content']
            date = post['date']
            db.insert_data((url, title, content, date))

    db.close_connection()
