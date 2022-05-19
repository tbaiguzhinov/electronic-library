import requests
import os


directory = "books"

for id_ in range(1, 11):
    url = f"https://tululu.org/txt.php?id={id_}"
    response = requests.get(url)
    response.raise_for_status() 
    filename = f"id{id_}.txt"
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(f"{directory}/{filename}", "wb") as file:
        file.write(response.content)