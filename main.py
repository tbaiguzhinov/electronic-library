import argparse
import json
import os
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests import ConnectionError, HTTPError


def check_for_redirect(response):
    if response.history:
        raise HTTPError
    return


def download_image(url, folder):
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
    response.raise_for_status()
    check_for_redirect(response)
    with open(file_path, "wb") as file:
        file.write(response.content)
    return file_path


def download_txt(id, url, filename, folder):
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
        response.raise_for_status()
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


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start_page",
        nargs='?',
        default=0,
        help="Начальный номер страницы",
        type=int,
        )
    parser.add_argument(
        "--end_page",
        nargs='?',
        default=702,
        help="Конечный номер страницы",
        type=int,
        )
    parser.add_argument(
        "--dest_folder",
        nargs='?',
        default="",
        help="Путь к каталогу с результатами парсинга: \
            картинкам, книгам, JSON",
        )
    parser.add_argument(
        "--skip_imgs",
        action="store_true",
        default=False,
        help="не скачивать картинки",
        )
    parser.add_argument(
        "--skip_txt",
        action="store_true",
        default=False,
        help="не скачивать книги",
        )
    parser.add_argument(
        "--json_path",
        nargs='?',
        default="all_books_info.json",
        help="указать свой путь к *.json файлу с результатами",
        )
    return parser.parse_args()


def main():
    args = get_args()
    args.json_path
    all_books = []
    for page in range(args.start_page, args.end_page):
        if page == 0:
            page = ""
        try:
            response = requests.get(
                f"https://tululu.org/l55/{page}",
                )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            links = soup.select("table div[id=content] div.bookimage")
            for link in links:
                short_link = link.select_one("a")["href"]
                response = requests.get(urljoin(response.url, short_link))
                response.raise_for_status()
                check_for_redirect(response)
                book_info, image_url = parse_book_page(response)
                book_title = book_info["title"]
                if not args.skip_txt:
                    book_path = download_txt(
                        id=short_link[2:-1],
                        url="https://tululu.org/txt.php",
                        filename=f"{book_title}",
                        folder=os.path.join(args.dest_folder, "books"),
                        )
                    if not book_path:
                        continue
                    book_info["book_path"] = book_path
                if not args.skip_imgs:
                    img_src = download_image(
                        url=image_url,
                        folder=os.path.join(args.dest_folder, "images"),
                        )
                    book_info["img_src"] = img_src
                all_books.append(book_info)
        except ConnectionError:
            print("Не удалось установить соединение с сервером")
            continue
        except HTTPError:
            print("Страница с указанным номером не найдена")
            continue
    with open(
            os.path.join(args.dest_folder, args.json_path),
            "w",
            encoding='utf8'
            ) as file:
        json.dump(all_books, file, ensure_ascii=False)

if __name__ == "__main__":
    main()
