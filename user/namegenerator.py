import re
import random 
import logging
import sqlite3
import requests
from bs4 import BeautifulSoup

class Parser:
    def get_words(self):
        """Парсит слова
        Добавляет в список nouns, если часть речи - существительное
        Добавляет в список adjectives, если часть речи - прилагательное
        Возвращает оба списка"""
        pattern = {"word": r"<td><b>([a-zA-Z]+) ?</b></td>",
                    "part of speech": r"<td>([a-zA-Z]+)</td>"}
        url = "https://satvocabulary.us/INDEX.ASP?CATEGORY=6000LIST"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "lxml")
        all_lines = [line for line in soup.body.find_all("tr")]
        nouns = []
        adjectives = []
        for line in all_lines[2:]:
            part = re.findall(pattern.get("part of speech"), str(line.contents[7]))
            word = re.findall(pattern.get("word"), str(line.contents[3]))
            if len(word) != 0 and len(part) != 0:
                if part[0] == "noun": 
                    nouns.append(word[0])
                elif part[0] == "adjective":
                    adjectives.append(word[0])
        return nouns, adjectives

class WordsDatabase:
    file_handler = logging.FileHandler(filename="sample.log")
    file_handler.setLevel(logging.ERROR)
    logging.root.handlers = [file_handler]

    def __init__(self):
        self.conn = self.create_connection()
        self.create_links_tables()

    def create_connection(self):
        """Создаёт объект подключения к базе данных и возвращает его
        В случае ошибки, записывает информацию о ней в лог-файл и пробрасывает ошибку дальше
          """
        try:
            conn = sqlite3.connect('words_database.db')
            if conn is None:
                raise Exception("Error! Can't create the database connection.")
            return conn
        except Exception as e:
            logging.error(str(e))
            raise

    def create_links_tables(self):
        """Создает таблицы в базе данных, если их не существует
        В случае ошибки, записывает информацию о ней в лог-файл и пробрасывает ошибку дальше
          """
        #2445 записей
        create_nouns_table = """ CREATE TABLE IF NOT EXISTS nouns (
                                                   id text PRIMARY KEY,
                                                   word text
                                               ); """
        #1914 записей
        create_adjective_table = """ CREATE TABLE IF NOT EXISTS adjectives (
                                                   id text PRIMARY KEY,
                                                   word text DEFAULT "None"
                                               ); """
        try:
            c = self.conn.cursor()
            c.execute(create_nouns_table)
            c.execute(create_adjective_table)
            print("создал таблицы")
        except Exception as e:
            logging.error(str(e))
            raise

    def insert_data_in_table(self, table_name, id, word):
        """Вставляет запись в таблицу
        В случае ошибки, записывает информацию о ней в лог-файл и пробрасывает ошибку дальше
          """
        try:
            c = self.conn.cursor()
            sql = "INSERT INTO " + table_name + " VALUES (?, ?)"
            c.execute(sql, [(id), (word)])
            self.conn.commit()
        except Exception as e:
            logging.error(str(e))
            raise

    def load_words_in_database(self, word_list, table_name):
        """Добавляет в таблицу table_name все значения из списка word_list"""
        ID = 0
        print("начал загружать слова")
        for word in word_list:
            self.insert_data_in_table(table_name, str(ID), word)
            print(ID)
            ID += 1
        print("закончил загружать слова")
        

    def get_data_from_table(self, table_name, id):
        """Получает слово из таблицы table_name по указанному id"""
        try:
            print("попытка поиска")
            c = self.conn.cursor()
            sql = "SELECT word FROM " + table_name + " WHERE id=?"
            res = c.execute(sql, [(id)]).fetchall()
            return res[0][0]
        except Exception as e:
            logging.error(str(e))
            raise

class NameGeneration:
    """Генерация имени"""
    @staticmethod
    def gen():
        """Генерирует случайное имя из прилагательного и существительного"""
        wordDB = WordsDatabase()
        noun_id = random.randint(0, 2445)
        adjective_id = random.randint(0, 1914)
        name = wordDB.get_data_from_table("adjectives", adjective_id)
        name += wordDB.get_data_from_table("nouns", noun_id)
        return name