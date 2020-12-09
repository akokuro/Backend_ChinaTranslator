from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import string
import requests
from bs4 import BeautifulSoup


class ParserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            bkrs = request.query_params["bkrs"]
            if bkrs == "True":
                bkrs = True
            else:
                bkrs = False
        except Exception:
            return Response(
                "В запрсое не указан параметр bkrs",
                400
            )
        try:
            zhonga = request.query_params["zhonga"]
            if zhonga == "True":
                zhonga = True
            else:
                zhonga = False
        except Exception:
            return Response(
                "В запрсое не указан параметр zhonga",
                400
            )
        try:
            text = request.data["text"]
        except Exception:
            return Response(
                "В запрсое не передан text",
                400
            )
        if not check_language_chinese(text):
            return Response(
                "Введите текст на китайском языке",
                400
            )

        result = Parser(text, bkrs, zhonga).result
        return Response(result, 200)


def check_language_chinese(text: str):
    punctuation_marks = string.punctuation + string.whitespace + '。［］【】﹁﹂『』「」﹁﹂………、‧《》〈〉﹏—～，1234567890'
    for char in text:
        if u'\u2E80' <= char <= u'\u2FD5':
            continue
        elif u'\u3190' <= char <= u'\u319f':
            continue
        elif u'\u3400' <= char <= u'\u4DBF':
            continue
        elif u'\u4E00' <= char <= u'\u9FCC':
            continue
        elif u'\uF900' <= char <= u'\uFAAD':
            continue
        elif char in punctuation_marks:
            continue
        else:
            return False
    return True


class Parser:
    url = {"bkrs": "https://bkrs.info/slovo.php?ch=", "zhonga": "https://www.zhonga.ru/search?q="}
    result = {}

    def __init__(self, text: str, bkrs: bool, zhonga: bool):
        self.text = text
        self.result = {}
        if bkrs:
            self.result["bkrs"] = self.parser_bkrs()
        if zhonga:
            self.result["zhonga"] = self.parser_zhonga()

    def parser_bkrs(self):
        if len(self.text)  > 100:
           return None
        link = Parser.url["bkrs"] + self.text
        response = requests.get(link)
        soup = BeautifulSoup(response.content, "lxml")
        result = []
        tables = soup.body("table", {"class": "tbl_bywords"})
        if len(tables) > 0:
            text = ""
            for i in soup.body("div", {"class": "fixed_scroll"}):
                text += i.text
            original_strings = []
            pinyin_strings = []
            translated_strings = []
            for table in tables:
                for count, row in enumerate(table('tr')):
                    for block in row('td'):
                        if block.center:
                            pinyin_strings.append([block.center.text])
                        if count % 2 == 0:
                            a = block('a')
                            original_strings.append(a[0].contents if len(a) > 0 else block.contents)
                        else:
                            a = block('a')

                            translated_strings.append(
                                [data.text.strip() for data in block('div')] if len(block('div')) > 0 else [
                                    block.text.strip()])
            for original, pinyin, translated in zip(original_strings, pinyin_strings, translated_strings):
                result.append([original, pinyin, translated])
        else:
            original = [self.text]
            pinyin = [soup.body.find("div", {"class": "py"}).text.strip()]
            translated = [t.text.strip() for t in soup.body("div", {"class": "ru"})]
            result.append(original)
            result.append(pinyin)
            result.append(translated)
        return result

    def parser_zhonga(self):
        if len(self.text) > 24:
            return None
        link = Parser.url["zhonga"] + self.text
        response = requests.get(link)
        original_strings = []
        pinyin_strings = []
        translated_strings = []
        soup = BeautifulSoup(response.content, "lxml")
        tables = soup.body("div", {"class": "segmented-unit"})
        result = []
        if len(tables) > 0:
            for string in tables:
                original_strings.append([string.find("div", {"class": "segmented-unit-value"}).a.text])
                pinyin_strings.append([string.find("span", {"class": "pinyin"}).text.strip()])
                translated_strings.append(
                    [string.find("div", {"class": "segmented-unit-dic-definitions"}).text.strip()])
            for original, pinyin, translated in zip(original_strings, pinyin_strings, translated_strings):
                result.append([original, pinyin, translated])
        else:
            original = [self.text]
            pinyin = [soup.body.find("span", {"class": "pinyin"}).text.strip()]
            translated = [t.text.strip() for t in soup.body("div", {"id": "unit-dic-definitions"})]
            result.append(original)
            result.append(pinyin)
            result.append(translated)
        return result
