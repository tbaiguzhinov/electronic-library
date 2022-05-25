import argparse
import os
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests import HTTPError, ConnectionError


def check_for_redirect(response):
    if response.url == "https://tululu.org/":
        raise HTTPError
    return


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
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{sanitize_filename(filename)}.txt")
    with open(file_path, "wb") as file:
        file.write(response.content)
    return file_path


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
    response.raise_for_status()
    with open(file_path, "wb") as file:
        file.write(response.content)
    return file_path


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
    image_link = soup.find("div", class_="bookimage").find("img")["src"]
    image_url = urljoin(response.url, image_link)
    comments_full = soup.find("div", id="content").find_all(class_="texts")
    comments_without_authors = [
        comment.find("span", class_="black").text for comment in comments_full
        ]
    title, author = soup.find("div", id="content").find("h1").text.split("::")
    genres_tags = soup.find("div",
                            id="content").find("span",
                                               class_="d_book").find_all("a")
    genres_names = [item.text for item in genres_tags]
    book_contents = {
        "image_url": image_url,
        "comments": comments_without_authors,
        "title": title.strip(),
        "author": author.strip(),
        "genres": genres_names
        }
    return book_contents


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "start_id",
        nargs='?',
        default=1,
        help="Начальный id книги",
        type=int
        )
    parser.add_argument(
        "end_id",
        nargs='?',
        default=5,
        help="Конечный id книги",
        type=int
        )
    args = parser.parse_args()
    for id_ in range(args.start_id, args.end_id+1):
        try:
            response = requests.get(f"https://tululu.org/b{id_}")
            check_for_redirect(response)
            response.raise_for_status()
            book_contents = parse_book_page(response)
            download_image(book_contents["image_url"])
            book_title = book_contents["title"]
            download_txt(
                id=id_,
                url="https://tululu.org/txt.php",
                filename=f"{id_}. {book_title}",
                folder="books/",
                )
        except HTTPError:
            print(f"Книга с id {id_} не найдена")
            continue
        except ConnectionError:
            print("Не удалось установить соединение с сервером")
            continue


if __name__ == "__main__":
    main()
