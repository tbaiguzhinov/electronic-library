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


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url)
    if response.ok:
        try:
            check_for_redirect(response)
        except HTTPError:
            print(f"Текст \"{filename}\" не найден")
            return
    else:
        return
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
    file_path = os.path.join(folder, f"{filename}")
    response = requests.get(url)
    if response.ok:
        with open(file_path, "wb") as file:
            file.write(response.content)
        return file_path
    else:
        return


def parse_book_page(content):
    """Функция для парсинга страницы книги.
    Args:
        content (str): Содержание страницы в виде текста.
    Returns:
        image_url (str): URL обложки книги.
        comments_without_authors (list): Список комментариев к книге.
        title (str): Название книги.
        author (str): Имя автора книги.
        genres_names (list): Список жанров книги.
    """
    soup = BeautifulSoup(content, 'lxml')
    image_link = soup.find("div", class_="bookimage").find("img")["src"]
    image_url = urljoin("https://tululu.org/", image_link)
    comments_full = soup.find("div", id="content").find_all(class_="texts")
    comments_without_authors = [
        comment.find("span", class_="black").text for comment in comments_full
        ]
    title, author = soup.find("div", id="content").find("h1").text.split("::")
    genres_tags = soup.find("div",
                            id="content").find("span",
                                               class_="d_book").find_all("a")
    genres_names = [item.text for item in genres_tags]
    return image_url, comments_without_authors, title.strip(), \
        author.strip(), genres_names


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("start_id", help="Начальный id книги", type=int)
    parser.add_argument("end_id", help="Конечный id книги", type=int)
    args = parser.parse_args()
    for id_ in range(args.start_id, args.end_id+1):
        try:
            response = requests.get(f"https://tululu.org/b{id_}")
        except ConnectionError:
            print("Не удалось установить соединение с сервером")
            return
        response.raise_for_status
        try:
            check_for_redirect(response)
        except HTTPError:
            print(f"Книга с id {id_} не найдена")
            continue
        image_url, comments_without_authors, title, \
            author, genres = parse_book_page(response.text)
        download_image(image_url)
        download_txt(url=f"https://tululu.org/txt.php?id={id_}",
                     filename=f"{id_}. {title}",
                     folder="books/",
                     )


if __name__ == "__main__":
    main()
