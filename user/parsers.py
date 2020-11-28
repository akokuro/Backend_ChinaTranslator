from rest_framework.parsers import BaseParser

class EverythingParser(BaseParser):
    """ Парсер """
    media_type = '*/*'

    def parse(self, stream, media_type=None, parser_context=None):
        """ Возвращает сырые данные запроса """
        return stream.read()