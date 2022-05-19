from bs4 import BeautifulSoup
import requests
from requests import HTTPError
import os

from pathvalidate import sanitize_filename

from urllib.parse import urljoin, urlparse, urlsplit, unquote

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
    try:
        check_for_redirect(response)
    except HTTPError:
        return
    if not os.path.exists(folder):
        os.makedirs(folder)
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
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = urlsplit(unquote(url)).path.split("/")[-1]
    file_path = os.path.join(folder, f"{filename}")
    response = requests.get(url)
    with open(file_path, "wb") as file:
        file.write(response.content)
    return file_path


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
    image_url = urljoin("https://tululu.org", image_link)
    comments_full = soup.find("div", id="content").find_all(class_="texts")
    comments_without_authors = [
        comment.find("span", class_="black").text for comment in comments_full
        ]
    title, author = soup.find("div", id="content").find("h1").text.split("::")
    genres_tags = soup.find("div", id="content").find("span", class_="d_book").find_all("a")
    genres_names = [item.text for item in genres_tags]
    return image_url, comments_without_authors, title, author, genres_names
    

def main():
    for id_ in range(1, 11):
        response = requests.get(f"https://tululu.org/b{id_}")
        try:
            check_for_redirect(response)
        except HTTPError:
            continue
        # download_image(image_url)
        
        # download_txt(url=f"https://tululu.org/txt.php?id={id_}",
        #              filename=f"{id_}. {title.strip()}",
        #              folder="books/",
        #              )
            
if __name__ == "__main__":
    main()
