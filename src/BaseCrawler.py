import datetime
from os import makedirs
from os.path import join, exists, basename
from re import sub, findall
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from markdownify import MarkdownConverter
from requests import get


class BaseCrawler:
    INTERNAL_LINK_REGEX = r'https://www\.jonathanpritchard\.me/([^\)]+)/?'
    FOLDERS_TO_CREATE = ['assets', 'categories', 'pages']
    TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:00"
    obsidian_path: str
    FOLDER_PAGES = "pages"
    FOLDER_CATEGORIES = "pages"
    FOLDER_ASSETS = "assets"

    def process_markdown(self, md_text):
        # Find all image urls using regex
        img_urls = findall(r'!\[.*?\]\((.*?)\)', md_text)

        for url in img_urls:
            if 'http' not in url:
                continue
            filename = self.download_and_save_image(url)
            if filename and url != filename:
                print(f"replacing '{url}' with '{filename}'")
                md_text = md_text.replace(url, filename)

        return md_text

    def download_and_save_image(self, img_url):
        # for that nth one time a layout broke
        if 'clicks.mlsend.com' in img_url:
            return img_url
        parsed_url = urlparse(img_url)
        filename = basename(parsed_url.path)
        filepath = join(self.obsidian_path, self.FOLDER_ASSETS, filename)
        if exists(filepath):
            return filename
        img_url = self.rewrite_old_domains(img_url)

        print(f"2. Downloading image from: {img_url}")
        response = get(img_url, stream=True)

        if response.status_code == 200:

            self.save_file(response.content, filepath, 'wb')
            return filename
        else:
            print(f"Unable to download image: {img_url}")
            return None

    @staticmethod
    def md(soup, **options):
        return MarkdownConverter(**options).convert_soup(soup)

    @staticmethod
    def get_meta_tags(page: BeautifulSoup) -> list:
        vals = page.find_all('meta', property='article:tag')
        if not vals:
            return []
        data = []
        for val in vals:
            if val['content'].isalnum() and val['content'].isupper():
                data.append(val['content'].replace(" ", ""))
            else:
                data.append(val['content'].title().replace(" ", ""))
        # print(f"tags: {data}")
        return data

    def convert_to_yaml(self, data: dict) -> str:
        base = "---\n"
        for key, value in data.items():
            if key in ['yaml', 'has_password', 'article_md']:
                continue
            if key in ['tags']:
                base += self.get_list_string('tags', value)
            elif key in ['yt_link']:
                if value:
                    base += f'{key}: {value}\n'
            elif key in ['publishing_date', 'publishing_week_number']:
                base += f'{key}: {value}\n'
            elif key in ['article_image_src']:
                base += f'{key}: "[[{value}]]"\n'
            else:
                nval = value.replace('"', '\\"')
                base += f'{key}: "{nval}"\n'
        base += "---\n"
        return base

    @staticmethod
    def get_list_string(list_name: str, tags: list) -> str:
        base = f"{list_name}:"
        for tag in tags:
            base += f"\n  - {tag}"
        return base + "\n"

    def create_folder_structure(self, start_path):
        for folder in self.FOLDERS_TO_CREATE:
            path = join(start_path, folder)
            makedirs(path, exist_ok=True)

    @staticmethod
    def save_file(content, path, mode='wb'):
        with open(path, mode) as f:
            f.write(content)

    @staticmethod
    def replace_slashes_with_dashes(match):
        group = match.group(1)
        replaced = group.replace('/', '-')
        return replaced[:-1] if replaced.endswith('-') else replaced

    def replace_links(self, text, is_markdown):
        replace_func = self.replace_slashes_with_dashes if is_markdown else lambda match: match.group(1).replace('/',
                                                                                                                 '-')[
                                                                                          :-1]
        new = sub(self.INTERNAL_LINK_REGEX, replace_func, text)
        return new

    def transform_links(self, text, is_markdown=True) -> str:
        return self.rewrite_old_domains(self.replace_links(text, is_markdown))

    @staticmethod
    def get_soup_from_url(url: str) -> BeautifulSoup:
        print(f"requesting url: {url}")
        return BeautifulSoup(get(url).content, 'html.parser')

    @staticmethod
    def get_meta_property(page, property_val) -> str:
        val = page.find('meta', property=property_val)
        if val:
            return val["content"]
        return ''

    @staticmethod
    def get_meta_name(page, name) -> str:
        val = page.find('meta', attrs={'name': name})
        if val:
            return val["content"]
        return ''

    def get_page_created_at(self, page):
        apt = self.get_meta_property(page, 'article:published_time')
        if not apt:
            apt = self.get_meta_property(page, 'og:updated_time')
        dt = datetime.datetime.fromisoformat(apt.replace("Z", "+00:00"))
        dt = dt.replace(tzinfo=None)
        result = dt.strftime(self.TIMESTAMP_FORMAT)

        # considering `result` is a tuple and datetime string is at 0th index
        if type(result) is tuple:
            return result[0]
        else:
            return result

    def rewrite_old_domains(self, text):
        return text.replace('likeamindreader.com', 'jonathanpritchard.me')

    def get_article_image(self, page, publishing_date: str, download_images=True):
        article_image_src = self.get_meta_property(page, 'og:image')
        filename = f"{publishing_date.replace(':', '-')}.jpeg" if "admin-ajax.php" in article_image_src else \
        article_image_src.split("/")[-1]
        article_image_file = f'{self.obsidian_path}/{self.FOLDER_ASSETS}/{filename}'
        if not exists(article_image_file) and download_images:
            print(f"1. Downloading image from: {self.rewrite_old_domains(article_image_src)}")
            content = get(self.rewrite_old_domains(article_image_src)).content
            print(f"Saving image to: {article_image_file}")

            self.save_file(content, article_image_file, 'wb')
        if download_images:
            article_image_src = filename
        return article_image_src

    def get_page_title(self, page):
        return self.get_meta_property(page, 'og:title').replace(' ⋆ Jonathan Pritchard', '')

    def get_page_description(self, page):
        return self.get_meta_property(page, 'og:description').replace('"', '\"')

    def get_page_url(self, page):
        return self.get_meta_property(page, 'og:url')

    def get_page_type(self, page):
        return self.get_meta_property(page, 'og:type').title()

    def get_time_to_read(self, page):
        return self.get_meta_name(page, 'twitter:data2')

    @staticmethod
    def get_page_prev_link(page):
        prev_post_link = page.find('a', class_='prev-post')
        prev_link = ''
        if prev_post_link and 'href' in prev_post_link.attrs:
            # print(f"next page is: {prev_post_link['href']}")
            prev_link = prev_post_link['href']
            prev_post_link.clear()
        return prev_link

    @staticmethod
    def get_page_next_link(page):
        next_post_link = page.find('a', class_='next-post')
        next_link = ''
        if next_post_link and 'href' in next_post_link.attrs:
            # print(f"previous page is: {next_post_link['href']}")
            next_link = next_post_link['href']
            next_post_link.clear()
        return next_link
