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
     

def main():
    for id_ in range(1, 11):
        response = requests.get(f"https://tululu.org/b{id_}")
        try:
            check_for_redirect(response)
        except HTTPError:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        book_image_link = soup.find("div", class_="bookimage").find("img")["src"]
        image_url = urljoin("https://tululu.org", book_image_link)
        comments = soup.find("div", id="content").find_all(class_="texts")
        title, author = soup.find("div", id="content").find("h1").text.split("::")
        print(title)
        for comment in comments:
            print(comment.find("span", class_="black").text)
        # download_image(image_url)
        
        # download_txt(url=f"https://tululu.org/txt.php?id={id_}",
        #              filename=f"{id_}. {title.strip()}",
        #              folder="books/",
        #              )
            
if __name__ == "__main__":
    main()
