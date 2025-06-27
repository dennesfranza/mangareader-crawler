#!/usr/bin/env python3

import os
import re
import argparse
import requests
from bs4 import BeautifulSoup

class MangaDownloader:
    BASE_URL = "http://www.mangareader.net"
    HEADERS = {'User-Agent': 'Mozilla/5.0'}

    def __init__(self, manga_name):
        self.manga_name = manga_name
        self.manga_url = f"{self.BASE_URL}/{self.manga_name}"

    def sanitize(self, name):
        return re.sub(r'[/\\:*?"<>|]', '.', name)

    def get_soup(self, url):
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")
            return None

    def download_image(self, img_url, save_path):
        try:
            response = requests.get(img_url, headers=self.HEADERS, stream=True)
            response.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"[OK] Downloaded {save_path}")
        except requests.RequestException as e:
            print(f"[ERROR] Failed to download image {img_url}: {e}")

    def download_page_image(self, page_url, folder):
        soup = self.get_soup(page_url)
        if not soup:
            return

        img_tag = soup.find('img')
        if img_tag and img_tag.get('src'):
            img_url = img_tag['src']
            filename = os.path.basename(img_url)
            save_path = os.path.join(folder, filename)
            if not os.path.exists(save_path):
                self.download_image(img_url, save_path)

    def process_chapter(self, chapter_href, root_folder):
        chapter_url = self.BASE_URL + chapter_href
        chapter_name = self.sanitize(chapter_href.strip('/'))
        chapter_folder = os.path.join(root_folder, chapter_name)

        if not os.path.exists(chapter_folder):
            os.makedirs(chapter_folder)

        soup = self.get_soup(chapter_url)
        if not soup:
            return

        options = soup.find_all('option')
        for option in options:
            page_value = option.get('value')
            if page_value:
                page_url = self.BASE_URL + page_value
                self.download_page_image(page_url, chapter_folder)

    def run(self):
        soup = self.get_soup(self.manga_url)
        if not soup:
            return

        listing = soup.find(id='listing')
        if not listing:
            print("[ERROR] Chapter listing not found.")
            return

        for a_tag in listing.find_all('a'):
            chapter_href = a_tag.get('href')
            if chapter_href:
                self.process_chapter(chapter_href, self.manga_name)

def main():
    parser = argparse.ArgumentParser(description='Download manga chapters from MangaReader using requests (no wget).')
    parser.add_argument('manga_name', help='Manga name as used in the URL (e.g., "naruto")')
    args = parser.parse_args()

    downloader = MangaDownloader(args.manga_name)
    downloader.run()

if __name__ == '__main__':
    main()
