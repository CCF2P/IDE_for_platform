from .analyzer import Analyzer, Text, Expression
from .sentiment import SentimentProvider

import re

def get_input() -> str:
    input_file = open(".\\Core\\Databases\\DB_Modules\\TuzovAnalyzer\\input.txt", "rb")
    input_data = input_file.read().decode("utf-8")
    input_file.close()
    return input_data


def sentiment_classifier(score):
    if score > 0.5:
        return "PSTV"
    elif score < -0.5:
        return "NGTV"
    else:
        return "NEUT"
    

def print_tree(children: list, elem=None, last=True, header='') -> None:
    elbow = "└──"
    pipe = "│  "
    tee = "├──"
    blank = "   "

    print(header + (elbow if last else tee) + elem.raw_words)

    if not children:
        return

    for i, c in enumerate(children):
        print_tree(
            children=c.children,
            elem=c,
            last=i == len(children) - 1,
            header=header + (blank if last else pipe)
        )


def get_input_by_path(path: str) -> str:
    try:
        input_file = open(path, "rb")
    except BaseException as e:
        print(f"{e}")
        return ""
    
    input_data = input_file.read().decode("utf-8")
    input_file.close()
    return input_data


def main(path: str=None):
    if path is not None:
        input_text = get_input_by_path(path)
    else:
        input_text = get_input()
    analyzer = Analyzer([SentimentProvider()])
    text = analyzer.analyse(input_text)

    for i in text.sentences:
        print_tree(children=i.expression.children, elem=i.expression)
    return text


class TuzovAnalyzer:
    def __init__(self, path: str=None) -> None:
        if path is not None:
            self.input_text = get_input_by_path(path)
        else:
            self.input_text = get_input()
        self.analyzer = Analyzer([SentimentProvider()])

    def analyze(self) -> Text:
        return self.analyzer.analyse(self.input_text)
    
    def get_class_expression(self) -> Expression:
        return Expression
    
    def prepare_text(self) -> None:
        '''
        Текст пользователя, пробразуется к виду:\n
        ``<предложение>(.?!)``\n
        ``<предложение>(.?!)``\n
        ``...``\n
        ``<последнее предложение>(.?!)`` перехода на новую строку нет\n
        Потом этот преобразованный текст записывается в файл ``input.txt``,\n
        который передается анализатору Тузова
        '''
        REGEX = r"(.*?[.!?])"
        sentences: list[str] = list()

        sentences = re.findall(REGEX, self.input_text)
        for i in range(len(sentences)):
            sentences[i] = sentences[i].lstrip()

        with open("input.txt", 'w', encoding="utf-8") as file:
            l = len(sentences)
            for i in range(l):
                if i != l - 1:
                    file.write(sentences[i] + '\n')
                else:
                    file.write(sentences[i])

    def _test(self) -> list[str]:
        with open(
            file="C:/Users/zhora/Desktop/Python/VKR_Platform/Core/Databases/DB_Modules/TuzovAnalyzer/input.txt",
            mode="r",
            encoding="utf8"
        ) as file:
            s = file.readlines()
        return s
