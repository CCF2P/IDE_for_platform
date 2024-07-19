# строчка ниже фиксит проблему с кодировкой
# -*- coding: utf-8 -*-
import re

#from analyzer import Analyzer, Expression
#from sentiment import SentimentProvider
from .SentenceTree import SentenceTree


"""
TODO: подлежащее может быть []
TODO: на будущее попробовать исправить была_собака и а_прыгала_и
"""


def get_input() -> str:
    input_file = open("input.txt", "rb")
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


def print_tree(children: list, elem=None, last=True, header=''):
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


def create_result_text(sentences: list) -> str:
    result: str = ""
    temp_sntc: str = ""
    for el in sentences:
        temp_sntc = ' '.join(el)
        result += temp_sntc + '. '
    return result


def main(tanalyzer):
    user_text = "Вдруг из леса выскочили волки. Мальчик по имени Петя кушал кашу. Она тоже испугалась и быстро помчалась по дороге. У дяди Семёна была хорошая лошадь. Мама купила ароматный, пышный, белый и большой цветок. Жучка испугалась и прыгнула в сани. Показались огни в окнах. Деревня была близко. С ним была собака Жучка. Волки отстали. Прыгнула в машину. Дядя Семён ехал из города домой. Белая ворона летала над вкусным сыром, а рыжая лиса бегала и прыгала за белой вороной. Высокая и красивая мама купила цветок, мороженое и подарок дочке. Береза росла, цвела и пахла. Мальчик покушал. Каждую осень птицы улетают на юг. Отец помыл машину на автомобильной мойке. Ночью в пруду громко квакают лягушки. Дети катаются на самокате. Я помогаю маме с уборкой."
    user_text2 = "Я всегда мечтал о большой собаке, с которой я смогу гулять и играть в парке. Пока я был ребёнком, у меня жил хомяк Хома. Я с детства хотел завести собаку, но родители мне не разрешали. Хома был очень маленький и пушистый. Его шерсть была средней длинны и коричневого цвета. Родители купили большую клетку для него, с двумя этажами. Я был очень рад, когда у меня появился маленький друг. Было очень весело смотреть как Хома бегает в колесе. Мне нравилось кормить его морковкой и орехами. Когда я вырос, и начал жить отдельно, я завел собаку. Теперь она у меня есть. Это большой и дружелюбный лабрадор. Я назвал его Джек. Мы с Джеком гуляем два раза в день. Он сделал мою жизнь более активной. С самого начала я обучаю его разным командам. Он уже умеет сидеть, лежать и прыгать. Мне нравится смотреть на Джека в солнечную погоду. Его золотая шерсть выглядит прекрасно на солнце. Джек это мой самый верный и лучший друг."
    tanalyzer.prepare_text()
    text = tanalyzer.analyze()

    sentences = list()
    for i in text.sentences:
        tree = SentenceTree(tanalyzer)
        tree.insert_from_words(
            cur_node=tree.root,
            words=i.expression.children,
            cur_word=i.expression
        )
        #tree.print_tree(tree.root)

        s = list()
        s = tree.test_summarize(
            cur_node=tree.root,
            sentence=s,
            depth=2
        )
        sentences.append(s)
    return create_result_text(sentences)


'''
Сравнение вывода деревьев Тузова и наших
for i in text.sentences:
        print_tree(i.expression.children, i.expression)

    for i in text.sentences:
        tree = SentenceTree()
        tree.insert_from_words(
            cur_node=tree.root,
            words=i.expression.children,
            cur_word=i.expression
        )
        trees.append(tree)

    print("=====================================\n")
    for i in trees:
        i.print_tree(i.root)
'''