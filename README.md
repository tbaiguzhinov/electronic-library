# Парсер книг с сайта tululu.org

Код осуществляет парсинг книги с сайта [tululu.org](https://tululu.org/),
скачивая изображение обложки в папку "`images`",
сам текст книги в папку "`books`" с названием файла в формате "`{идентификационный номер книги}. {название книги}`". 

### Как установить

Python3 должен быть уже установлен.
* Скачайте код
* Установите зависимости  
`pip install -r requirements.txt`
* Запустите программу командой  
`python3 main.py`

### Аргументы

Код принимает два выборочных аргумента: `start_page` и `end_page`,
которые обозначают идентификационный номер первой книги и идентификационный номер последней книги для скачивания.  
К примеру, для скачивания книг с идентификационными номерами с 15 по 25, необходимо ввести команду:  
`python3 main.py 15 25`
По умолчанию, команда `python3 main.py` выполняет загрузку книг с идентификационными номерами с 1 до 5 включительно.

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
