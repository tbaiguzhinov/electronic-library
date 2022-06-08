import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server #, shell

def create_index():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    with open("all_books_info.json", "r", encoding="utf8") as file:
        books = json.loads(file.read().replace("\\\\", "/"))
    rendered_page = template.render(
        books=books,
    )
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    create_index()
    server = Server()
    server.watch("template.html", create_index) #shell("make html", cwd='docs'))
    server.serve()
    

if __name__ == "__main__":
    main()
