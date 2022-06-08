import json
import os
import math

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def create_index():
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html", "xml"])
    )
    template = env.get_template("template.html")
    with open("all_books_info.json", "r", encoding="utf8") as file:
        books = json.loads(file.read().replace("\\\\", "/"))
    index_page_folder = "pages"
    os.makedirs(index_page_folder, exist_ok=True)
    book_pages = list(chunked(books, 20))
    pages_quantity = math.ceil(len(books)/20)
    for num, book_page in enumerate(book_pages, 1):
        rendered_page = template.render(
            current_page=num,
            pages_quantity=pages_quantity,
            books=list(chunked(book_page, 2)),
        )
        with open(
                f"{index_page_folder}\index{num}.html",
                mode="w",
                encoding="utf8"
                ) as file:
            file.write(rendered_page)


def main():
    create_index()
    server = Server()
    server.watch("template.html", create_index)
    server.serve()


if __name__ == "__main__":
    main()
