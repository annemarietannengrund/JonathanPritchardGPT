import os

from bs4 import BeautifulSoup

from src.BaseCrawler import BaseCrawler


class JonathanPritchardCrawler(BaseCrawler):
    LIST_ARTICLE_LINKS = ('main#brx-content section.brxe-section div.brxe-container div.brxe-block'
                          ' div.brxe-block h3.brxe-heading a')
    ARTICLE_CONTENT = '#brx-content > .brxe-section > .brxe-container'
    BLOG_PAGING_URL = "https://www.jonathanpritchard.me/blog/page/{}/"

    def __init__(self, obsidian_path):
        self.obsidian_path = obsidian_path

    @staticmethod
    def get_obsidian_link(link: str):
        if not link:
            return ''
        return f'[[{link}]]'

    def get_article_category(self, article: BeautifulSoup, page_type: str):
        category = article.select_one('div.brxe-post-meta > span.item > a')
        category_link = ""
        if category:
            category_link = category.get("href")
            filename = f'obsidian/categories/{self.transform_links(category_link, is_markdown=False)}.md'
            if not os.path.exists(filename):
                content = f"""---\npage_type: "[[Category]]"\nfor_type: "{page_type}"\ntags:\n  - Category\n---\n"""
                content += "\n".join([
                    f'# Last 10 posts in {category.text} {page_type}\'s posts',
                    '```dataview',
                    'TABLE publishing_date, page_url',
                    'FROM [[]]',
                    'SORT publishing_date DESC',
                    'LIMIT 10',
                    '```'
                ])
                self.save_file(content, filename, 'w')
        return self.transform_links(category_link, is_markdown=False)

    @staticmethod
    def has_password(page: BeautifulSoup) -> bool:
        return True if page.select_one('#brx-content > article.brxe-container > form.post-password-form') else False

    @staticmethod
    def update_article_image_path(article: BeautifulSoup, article_image_src: str):
        article_image = article.select_one('img.brxe-image')
        if not article_image:
            article_image = article.select_one('figure.wp-block-image img')
        if not article_image:
            article_image = article.select_one('figure.brxe-image img')
        if not article_image:
            div_to_replace = article.find('figure', {'class': 'wp-block-embed-youtube'})
            if div_to_replace:
                new_img = BeautifulSoup('', 'html.parser').new_tag('img')
                new_img['src'] = article_image_src
                div_to_replace.replace_with(new_img)
            else:
                new_img = BeautifulSoup('', 'html.parser').new_tag('img')
                new_img['src'] = article_image_src
                article.insert(0, new_img)
        if article_image and article_image_src:
            #print(f"replacing article image src {article_image['src']} with {article_image_src}")
            article_image['src'] = article_image_src

    @staticmethod
    def delete_elements(article: BeautifulSoup):
        needles = ['bricks-lazy-hidden', 'brxe-shortcode']
        for needle in needles:
            trashs = article.find_all('div', class_=needle)
            for trash in trashs:
                trash.clear()

    def find_youtube_embedding(self, article: BeautifulSoup):
        yt_link = article.select_one('a.ytp-title-link')
        if not yt_link:
            return ''
        return yt_link['href']
    def get_article_details(self, page: BeautifulSoup, data: dict) -> dict:
        if self.has_password(page):
            return {'article_md': '', 'page_category': ''}
        article = page.select_one(self.ARTICLE_CONTENT)
        yt_link = self.find_youtube_embedding(article)
        self.delete_elements(article)
        self.update_article_image_path(article, data.get('article_image_src'))
        article_md = self.process_markdown(self.md(article).replace('::', ':'))
        article_md = self.transform_links(article_md)
        return {
            'page_category': f"[[{self.get_article_category(article, data.get('page_type'))}]]",
            'article_md': article_md,
            'yt_link': yt_link
        }

    def get_page_metadata(self, soup: BeautifulSoup, download_images=True) -> dict:
        publishing_date = self.get_page_created_at(soup)
        article_image_src = self.get_article_image(soup, publishing_date, download_images)
        data = {
            'publishing_date': publishing_date,
            'article_image_src': article_image_src,
            'page_title': self.get_page_title(soup),
            'page_description': self.get_page_description(soup),
            'page_url': self.get_page_url(soup),
            'page_type': f'[[{self.get_page_type(soup)}]]',
            'time_to_read': self.get_time_to_read(soup),
            'next_file': self.get_obsidian_link(self.transform_links(self.get_page_next_link(soup), False)),
            'prev_file': self.get_obsidian_link(self.transform_links(self.get_page_prev_link(soup), False)),
            'tags': self.get_meta_tags(soup)
        }
        article_details = self.get_article_details(soup, data)
        data.update(article_details)
        return data

    def crawl_blog(self, url):
        save_path = os.path.join(self.obsidian_path, self.FOLDER_PAGES, f"{self.transform_links(url, False)}.md")
        if os.path.exists(save_path):
            print(f"File already exists, skipping {save_path}")
            return
        soup = self.get_soup_from_url(url)
        page_meta = self.get_page_metadata(soup)
        yaml = self.convert_to_yaml(page_meta)
        self.save_file(yaml + page_meta.get('article_md'), save_path, 'w')

    def process_page(self, page) -> bool:
        article_links = page.select(self.LIST_ARTICLE_LINKS)
        if not article_links:
            return False
        for link in article_links:
            if not link or 'href' not in link.attrs:
                continue
            self.crawl_blog(link['href'])
        return True

    def iterate_blog_pages(self, startpage:int):
        start = startpage
        while self.process_page(self.get_soup_from_url(self.BLOG_PAGING_URL.format(start))):
            start += 1

    def main(self, startpage=1):
        self.create_folder_structure(self.obsidian_path)
        #self.iterate_blog_pages(startpage)
        exit(11)
        # im lazy, here are some hardcoded urls
        urls = [
            'https://www.jonathanpritchard.me/corporate-services/trade-show/',
            'https://www.jonathanpritchard.me/author/',
            'https://www.jonathanpritchard.me/corporate-services/corporate-speaking/',
            'https://www.jonathanpritchard.me/corporate-services/'
        ]
        for url in urls:
            self.crawl_blog(url)