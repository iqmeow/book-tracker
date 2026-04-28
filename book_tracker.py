import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("900x600")
        
        # Данные
        self.books = []
        self.filtered_books = []
        
        # Загрузка сохраненных данных
        self.load_data()
        
        # Создание интерфейса
        self.create_input_frame()
        self.create_table_frame()
        self.create_filter_frame()
        
        # Обновление таблицы
        self.refresh_table()
    
    def create_input_frame(self):
        """Фрейм для ввода данных книги"""
        input_frame = tk.LabelFrame(self.root, text="Добавление новой книги", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Название книги
        tk.Label(input_frame, text="Название книги:").grid(row=0, column=0, sticky="w")
        self.title_entry = tk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Автор
        tk.Label(input_frame, text="Автор:").grid(row=0, column=2, sticky="w")
        self.author_entry = tk.Entry(input_frame, width=25)
        self.author_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Жанр
        tk.Label(input_frame, text="Жанр:").grid(row=1, column=0, sticky="w")
        self.genre_entry = tk.Entry(input_frame, width=30)
        self.genre_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Количество страниц
        tk.Label(input_frame, text="Количество страниц:").grid(row=1, column=2, sticky="w")
        self.pages_entry = tk.Entry(input_frame, width=25)
        self.pages_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Кнопка добавления
        tk.Button(input_frame, text="➕ Добавить книгу", command=self.add_book, 
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).grid(row=2, column=0, columnspan=4, pady=10)
    
    def create_table_frame(self):
        """Фрейм для таблицы с книгами"""
        table_frame = tk.LabelFrame(self.root, text="Список прочитанных книг", padx=10, pady=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создание таблицы Treeview
        columns = ("Название", "Автор", "Жанр", "Страницы")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Настройка колонок
        self.tree.heading("Название", text="Название книги")
        self.tree.heading("Автор", text="Автор")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Страницы", text="Страницы")
        
        self.tree.column("Название", width=250)
        self.tree.column("Автор", width=200)
        self.tree.column("Жанр", width=150)
        self.tree.column("Страницы", width=100)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления
        btn_frame = tk.Frame(table_frame)
        btn_frame.pack(fill="x", pady=10)
        
        tk.Button(btn_frame, text="🗑 Удалить выбранную", command=self.delete_book, 
                 bg="#f44336", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="💾 Сохранить в JSON", command=self.save_to_json, 
                 bg="#2196F3", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="📂 Загрузить из JSON", command=self.load_from_json, 
                 bg="#FF9800", fg="white").pack(side="left", padx=5)
    
    def create_filter_frame(self):
        """Фрейм для фильтрации"""
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация книг", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по жанру
        tk.Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, sticky="w")
        self.genre_filter = tk.Entry(filter_frame, width=25)
        self.genre_filter.grid(row=0, column=1, padx=5)
        self.genre_filter.bind('<KeyRelease>', lambda e: self.apply_filters())
        
        # Фильтр по страницам
        tk.Label(filter_frame, text="Страниц больше:").grid(row=0, column=2, sticky="w")
        self.pages_filter = tk.Entry(filter_frame, width=10)
        self.pages_filter.grid(row=0, column=3, padx=5)
        self.pages_filter.bind('<KeyRelease>', lambda e: self.apply_filters())
        
        # Кнопка сброса
        tk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters, 
                 bg="#9E9E9E", fg="white").grid(row=0, column=4, padx=20)
        
        # Статистика
        self.stats_label = tk.Label(filter_frame, text="", fg="blue")
        self.stats_label.grid(row=1, column=0, columnspan=5, pady=5)
    
    def add_book(self):
        """Добавление новой книги"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages = self.pages_entry.get().strip()
        
        # Проверка на пустые поля
        if not title or not author or not genre or not pages:
            messagebox.showwarning("Ошибка", "Все поля должны быть заполнены!")
            return
        
        # Проверка, что количество страниц - число
        try:
            pages = int(pages)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Количество страниц должно быть положительным числом!")
            return
        
        # Добавление книги
        book = {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages,
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.books.append(book)
        self.save_data()  # Автосохранение
        self.clear_input_fields()
        self.apply_filters()
        messagebox.showinfo("Успех", f"Книга '{title}' добавлена!")
    
    def delete_book(self):
        """Удаление выбранной книги"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите книгу для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную книгу?"):
            # Получаем индекс выбранной книги
            for item in selected:
                item_text = self.tree.item(item, "values")
                # Ищем книгу в оригинальном списке
                for i, book in enumerate(self.books):
                    if (book["title"] == item_text[0] and 
                        book["author"] == item_text[1] and
                        book["genre"] == item_text[2] and
                        str(book["pages"]) == item_text[3]):
                        del self.books[i]
                        break
            
            self.save_data()
            self.apply_filters()
            messagebox.showinfo("Успех", "Книга удалена!")
    
    def apply_filters(self):
        """Применение фильтров"""
        genre_filter = self.genre_filter.get().strip().lower()
        pages_filter = self.pages_filter.get().strip()
        
        self.filtered_books = self.books.copy()
        
        # Фильтр по жанру
        if genre_filter:
            self.filtered_books = [b for b in self.filtered_books 
                                  if genre_filter in b["genre"].lower()]
        
        # Фильтр по страницам
        if pages_filter:
            try:
                min_pages = int(pages_filter)
                self.filtered_books = [b for b in self.filtered_books 
                                      if b["pages"] > min_pages]
            except ValueError:
                pass
        
        # Обновление статистики
        total_books = len(self.books)
        shown_books = len(self.filtered_books)
        total_pages = sum(b["pages"] for b in self.books)
        
        self.stats_label.config(
            text=f"📚 Всего книг: {total_books} | Показано: {shown_books} | 📖 Всего страниц: {total_pages}"
        )
        
        self.refresh_table()
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.genre_filter.delete(0, tk.END)
        self.pages_filter.delete(0, tk.END)
        self.apply_filters()
    
    def refresh_table(self):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполнение таблицы
        for book in self.filtered_books:
            self.tree.insert("", "end", values=(
                book["title"],
                book["author"],
                book["genre"],
                book["pages"]
            ))
    
    def clear_input_fields(self):
        """Очистка полей ввода"""
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)
    
    def save_to_json(self):
        """Сохранение в JSON файл"""
        file_path = f"books_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в файл: {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
    
    def load_from_json(self):
        """Загрузка из JSON файла"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Выберите JSON файл",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_books = json.load(f)
                
                # Проверка структуры данных
                for book in loaded_books:
                    if all(k in book for k in ["title", "author", "genre", "pages"]):
                        self.books.append(book)
                
                self.save_data()
                self.apply_filters()
                messagebox.showinfo("Успех", f"Загружено {len(loaded_books)} книг!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")
    
    def save_data(self):
        """Автосохранение данных в books.json"""
        try:
            with open("books.json", 'w', encoding='utf-8') as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка автосохранения: {e}")
    
    def load_data(self):
        """Автозагрузка данных из books.json"""
        if os.path.exists("books.json"):
            try:
                with open("books.json", 'r', encoding='utf-8') as f:
                    self.books = json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки: {e}")
                self.books = []
        else:
            # Пример данных для демонстрации
            self.books = [
                {"title": "Война и мир", "author": "Лев Толстой", "genre": "Роман", "pages": 1300, "date_added": "2024-01-01"},
                {"title": "Преступление и наказание", "author": "Фёдор Достоевский", "genre": "Роман", "pages": 670, "date_added": "2024-01-02"},
                {"title": "Мастер и Маргарита", "author": "Михаил Булгаков", "genre": "Фантастика", "pages": 480, "date_added": "2024-01-03"}
            ]

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()