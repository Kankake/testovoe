import json
import os

class BookError(Exception):
    """Базовый класс для исключений, связанных с книгами."""
    pass

class BookNotFoundError(BookError):
    """Исключение, возникающее когда книга не найдена."""
    pass

class InvalidInputError(BookError):
    """Исключение, возникающее при неверном вводе."""
    pass

class InvalidStatusError(BookError):
    """Исключение, возникающее при неверном статусе книги."""
    pass

class Book:
    """Класс, представляющий книгу в библиотеке."""

    def __init__(self, title: str, author: str, year: int, status: str = 'в наличии', id: int = None):
        """
        Инициализирует новый экземпляр книги.
        """
        self.id = id
        self.title = title
        self.author = author
        self.year = year
        if status not in ['в наличии', 'выдана']:
            raise InvalidStatusError("Неверный статус книги")
        self.status = status

    def to_dict(self):
        """
        Преобразует объект книги в словарь.
        """
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'status': self.status
        }

class Library:
    def __init__(self):
        self.books = []
        self.next_id = 1
        self.data_folder = os.path.join(os.path.dirname(__file__), 'data')
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        self.data_file = os.path.join(self.data_folder, 'library_data.json')
        self.load_data()
        self.save_data()

    def save_data(self) -> None:
        """Сохраняет данные библиотеки в JSON файл."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([book.to_dict() for book in self.books], f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Ошибка при сохранении данных: {e}")

    def load_data(self) -> None:
        """Загружает данные библиотеки из JSON файла."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.books = []
                for book_data in data:
                    book = Book(
                        title=book_data['title'],
                        author=book_data['author'],
                        year=book_data['year'],
                        status=book_data['status'],
                        id=book_data['id']
                    )
                    self.books.append(book)
                if self.books:
                    self.next_id = max(book.id for book in self.books) + 1
                else:
                    self.next_id = 1
        except FileNotFoundError:
            self.books = []
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка при чтении данных: {e}")
            self.books = []


    def add_book(self, book_or_title, author: str = None, year: int = None) -> Book:
        """
        Добавляет новую книгу в библиотеку.

        :book_or_title: Объект Book или название книги
        """
        if isinstance(book_or_title, Book):
            book = book_or_title
            if not book.title or not book.author or not book.year:
                raise InvalidInputError("Все поля должны быть заполнены")
            if not isinstance(book.year, int):
                raise InvalidInputError("Год должен быть числом")
        else:
            if not book_or_title or not author or not year:
                raise InvalidInputError("Все поля должны быть заполнены")
            try:
                year = int(year)
            except ValueError:
                raise InvalidInputError("Год должен быть числом")
            book = Book(book_or_title, author, year)
        
        book.id = self.next_id
        self.next_id += 1
        self.books.append(book)
        self.save_data()
        return book

    def delete_book(self, id: int) -> None:
        """
        Удаляет книгу из библиотеки по ID.
        """
        original_length = len(self.books)
        self.books = [book for book in self.books if book.id != id]
        if len(self.books) == original_length:
            raise BookNotFoundError(f"Книга с ID {id} не найдена")
        self.save_data()

    def search_book(self, title: str = None, author: str = None, year: int = None) -> list[Book]:
        """
        Ищет книги в библиотеке по заданным критериям.
        """
        results = self.books

        if title is not None:
            if not isinstance(title, str):
                raise TypeError("Название должно быть строкой")
            results = [book for book in results if title.lower() in book.title.lower()]

        if author is not None:
            if not isinstance(author, str):
                raise TypeError("Автор должен быть строкой")
            results = [book for book in results if author.lower() in book.author.lower()]

        if year is not None:
            if not isinstance(year, int):
                raise TypeError("Год должен быть числом")
            results = [book for book in results if book.year == year]

        return results

    def change_status(self, id: int, status: str) -> None:
        """
        Изменяет статус книги.
        """
        if status not in ['в наличии', 'выдана']:
            raise InvalidStatusError("Неверный статус книги")
        for book in self.books:
            if book.id == id:
                book.status = status
                self.save_data()
                return
        raise BookNotFoundError(f"Книга с ID {id} не найдена")

    def view_books(self) -> None:
        """Выводит список всех книг в библиотеке."""
        if not self.books:
            print("Библиотека пуста")
        for book in self.books:
            print(f"ID: {book.id}, Название: {book.title}, Автор: {book.author}, "
                  f"Год: {book.year}, Статус: {book.status}")

class LibraryInterface:
    """Класс, представляющий интерфейс для взаимодействия с библиотекой."""

    def __init__(self):
        """Инициализирует новый экземпляр интерфейса библиотеки."""
        self.library = Library()

    def run(self) -> None:
        """Запускает интерактивный интерфейс библиотеки."""
        print('\n1. Добавить книгу')
        print('2. Удалить книгу')
        print('3. Поиск книги')
        print('4. Изменение статуса книги')
        print('5. Вывести список книг')
        print('6. Выход')
        choice = input('Выберите действие: ')
        
        if choice == '6':
            print("Выход из программы.")
            return

        try:
            if choice == '1':
                self.add_book()
            elif choice == '2':
                self.delete_book()
            elif choice == '3':
                self.search_book()
            elif choice == '4':
                self.change_status()
            elif choice == '5':
                self.library.view_books()
            else:
                print("Неверный выбор. Пожалуйста, выберите число от 1 до 6.")
        except BookError as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Произошла неожиданная ошибка: {e}")
        
        self.run()

    def add_book(self) -> None:
        """Обрабатывает добавление новой книги"""
        title = input('Введите название книги: ')
        author = input('Введите автора книги: ')
        year = input('Введите год издания книги: ')
        try:
            self.library.add_book(title, author, year)
            print("Книга успешно добавлена")
        except InvalidInputError as e:
            print(f"Ошибка при добавлении книги: {e}")

    def delete_book(self) -> None:
        """Обрабатывает удаление книги"""
        try:
            id = int(input('Введите id книги: '))
            self.library.delete_book(id)
            print("Книга успешно удалена")
        except ValueError:
            print("ID должен быть числом")
        except BookNotFoundError as e:
            print(e)

    def search_book(self) -> None:
        """Обрабатывает поиск книги"""
        print('1. Поиск по названию')
        print('2. Поиск по автору')
        print('3. Поиск по году издания')
        choice = input('Выберите действие: ')
        try:
            if choice == '1':
                title = input('Введите название книги: ')
                results = self.library.search_book(title=title)
            elif choice == '2':
                author = input('Введите автора книги: ')
                results = self.library.search_book(author=author)
            elif choice == '3':
                year = int(input('Введите год издания книги: '))
                results = self.library.search_book(year=year)
            else:
                print("Неверный выбор")
                return
            if not results:
                print("Книги не найдены")
            for book in results:
                print(f"ID: {book.id}, Название: {book.title}, Автор: {book.author}, "
                      f"Год: {book.year}, Статус: {book.status}")
        except ValueError:
            print("Год должен быть числом")
        except TypeError as e:
            print(f"Ошибка при поиске: {e}")

    def change_status(self) -> None:
        """Обрабатывает изменение статуса книги"""
        try:
            id = int(input('Введите id книги: '))
            new_status = input('Введите статус книги (выдана/в наличии): ').lower()
            self.library.change_status(id, new_status)
            print("Статус книги успешно изменен")
        except ValueError:
            print("ID должен быть числом")
        except (BookNotFoundError, InvalidStatusError) as e:
            print(e)

if __name__ == "__main__":
    interface = LibraryInterface()
    interface.run()
