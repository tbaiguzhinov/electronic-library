import requests
import os
import json

from bs4 import BeautifulSoup
from requests import HTTPError, ConnectionError
from urllib.parse import urljoin, unquote, urlsplit
from pathvalidate import sanitize_filename

def check_for_redirect(response):
    response.raise_for_status()
    if response.status_code == 301:
        raise HTTPError
    return


def download_image(url, folder='images/'):
    """Функция для скачивания изображений.
    Args:
        url (str): Cсылка на изображение, которое хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    os.makedirs(folder, exist_ok=True)
    filename = urlsplit(unquote(url)).path.split("/")[-1]
    file_path = os.path.join(folder, filename)
    response = requests.get(url)
    check_for_redirect(response)
    with open(file_path, "wb") as file:
        file.write(response.content)
    return file_path


def download_txt(id, url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    params = {"id": id}
    try:
        response = requests.get(url, params=params)
        check_for_redirect(response)
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, f"{sanitize_filename(filename)}.txt")
        with open(file_path, "wb") as file:
            file.write(response.content)
        return file_path
    except HTTPError:
        return None


def parse_book_page(response):
    """Функция для парсинга страницы книги.
    Args:
        content (str): Содержание страницы в виде текста.
    Returns:
        dict with keys:
        - image_url (str): URL обложки книги.
        - comments (list): Список комментариев к книге.
        - title (str): Название книги.
        - author (str): Имя автора книги.
        - genres (list): Список жанров книги.
    """
    soup = BeautifulSoup(response.text, 'lxml')
    image_link = soup.select_one("div.bookimage img")["src"]
    image_url = urljoin(response.url, image_link)
    comments_full = soup.select("div[id=content] div.texts")
    comments_without_authors = [
        comment.select_one("span.black").text for comment in comments_full
        ]
    title, author = soup.select_one("div[id=content] h1").text.split("::")
    genres_tags = soup.select("div[id=content] span.d_book a")
    genres_names = [item.text for item in genres_tags]
    book_contents = {
        "title": title.strip(),
        "author": author.strip(),
        "comments": comments_without_authors,
        "genres": genres_names
        }
    return book_contents, image_url

all_books = []
for page in range(0, 1):
    if page == 0:
        page = ""
    try:
        response = requests.get(
            f"https://tululu.org/l55/{page}",
            )
        response.raise_for_status
        soup = BeautifulSoup(response.text, 'lxml')
        links = soup.select("table div[id=content] div.bookimage")
        for link in links:
            short_link = link.select_one("a")["href"]
            response = requests.get(urljoin(response.url, short_link))
            check_for_redirect(response)
            book_info, image_url = parse_book_page(response)
            book_title = book_info["title"]
            book_path = download_txt(
                id=short_link[2:-1],
                url="https://tululu.org/txt.php",
                filename=f"{book_title}",
                folder="books/",
                )
            if not book_path:
                continue
            ims_src = download_image(image_url)
            book_info["book_path"] = book_path
            book_info["ims_src"] = ims_src
            all_books.append(book_info)
    except ConnectionError:
        print("Не удалось установить соединение с сервером")
        continue

with open("all_books_info.json", "w", encoding='utf8') as file:
    json.dump(all_books, file, ensure_ascii=False)