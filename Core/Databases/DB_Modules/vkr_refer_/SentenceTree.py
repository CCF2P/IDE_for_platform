# строчка ниже фиксит проблему с кодировкой
# -*- coding: utf-8 -*-
#from analyzer import Expression
import re


class SentenceTreeNode:
    def __init__(self, leaf: bool = False) -> None:
        self.leaf = leaf
        self.word = ""
        self.props = []
        self.depth = 0
        self.child = []


class SentenceTree:
    def __init__(self, tanalyzer) -> None:
        self.root = SentenceTreeNode(True)

    @staticmethod
    def get_part_of_speech(node: SentenceTreeNode) -> list[str]:
        '''
        В узле дерева, в поле data хранится список вида:
        ``[<свойства слова>]``, где\n
        ``<свойства слова>`` - падеж, род и т.п. из анализатора Тузова
        
        Функция возвращает ``[]``, если текущий узел дерева - корень.\n
        Иначе функция возвращает ``["<часть речи>"]``
        '''
        if node is None:
            return None

        r = r"\{([а-яА-Я]+)\."
        return re.findall(r, node.props[2])

    def print_tree(
        self,
        cur_node: SentenceTreeNode,
        last: bool = True,
        header: str = ''
    ) -> None:
        elbow = "└──"
        pipe = "│  "
        tee = "├──"
        blank = "   "

        print(
            header + \
            (elbow if last else tee) + cur_node.word + \
            " - " + f"{self.get_part_of_speech(cur_node)}"
        )

        if not cur_node.child:
            return

        for i, c in enumerate(cur_node.child):
            self.print_tree(
                cur_node=c,
                last=i == len(cur_node.child) - 1,
                header=header + (blank if last else pipe)
            )

    def insert_from_words(
        self,
        cur_node: SentenceTreeNode,
        words: list,
        cur_word = None,
        last: bool = True,
        cur_depth: int = 0
    ) -> None:
        if cur_node.child == []:
            cur_node.word = cur_word.raw_words
            cur_node.props = cur_word.properties
            cur_node.depth = cur_depth

        if not words:
            cur_depth = 0
            return

        for i, c in enumerate(words):
            new_node = SentenceTreeNode()
            cur_node.child.append(new_node)

            self.insert_from_words(
                cur_node=new_node,
                words=c.children,
                cur_word=c,
                last=i == len(words) - 1,
                cur_depth=cur_depth + 1
            )

    def test_summarize(
        self,
        cur_node: SentenceTreeNode,
        sentence: list,
        depth: int,
        parent: SentenceTreeNode = None
    ) -> list[str]:
        # Убираем предлоги, которые ниже заданной глубины
        # бессвязные предлоги (прыгнула за/пошла по)
        if cur_node.depth > depth:
            if self.get_part_of_speech(parent) == ["Предлог"]:
                if parent.word in sentence:
                    sentence.remove(parent.word)
            return sentence

        if (
            self.get_part_of_speech(parent) == [] or \
            self.get_part_of_speech(parent) == ["Глагол"]
        ):
            # проверка на подлежащее
            if cur_node == parent.child[0]:
                # подлежащим может быть сущв, мест, []
                # [] - значит имя, название и тп
                if (
                    self.get_part_of_speech(cur_node) == ["Сущв"] or \
                    self.get_part_of_speech(cur_node) == ["Мест"] or \
                    self.get_part_of_speech(cur_node) == []
                ):
                    sentence.append(cur_node.word)
                    if parent.word not in sentence:
                        sentence.append(parent.word)

                # "подлежащим" может быть предлог, поэтому надо добавить
                if self.get_part_of_speech(cur_node) == ["Предлог"]:
                    if parent.word in sentence:
                        sentence.append(cur_node.word)
                    else:
                        sentence.append(parent.word)
                        sentence.append(cur_node.word)

            # проверка на дополнение, обстоятельство и тп
            # проверка остальных членов предложения
            else:
                # сказуемое -> сущв (не подлежащее)
                if self.get_part_of_speech(cur_node) == ["Сущв"]:
                    if parent.word in sentence:
                        sentence.append(cur_node.word)
                    else:
                        sentence.append(parent.word)
                        sentence.append(cur_node.word)

                # сказуемое -> глагол (сказуемое/нет)
                if self.get_part_of_speech(cur_node) == ["Глагол"]:
                    sentence.append(cur_node.word)

                # сказуемое -> предлог
                if self.get_part_of_speech(cur_node) == ["Предлог"]:
                    if parent.word not in sentence:
                        sentence.append(parent.word)
                    sentence.append(cur_node.word)

        # проверка на сущв -> сущв/предлог/прил
        if self.get_part_of_speech(parent) == ["Сущв"]:
            if self.get_part_of_speech(cur_node) == ["Сущв"]:
                sentence.append(cur_node.word)

            # существительное -> предлог
            if self.get_part_of_speech(cur_node) == ["Предлог"]:
                i = sentence.index(parent.word)
                sentence.insert(i + 1, cur_node.word)

            if self.get_part_of_speech(cur_node) == ["Прил"]:
                i = sentence.index(parent.word)
                if i == 0:
                    sentence.insert(0, cur_node.word)
                else:
                    sentence.insert(i, cur_node.word)

        # проверка на прил -> прил/сущв
        if self.get_part_of_speech(parent) == ["Прил"]:
            i = sentence.index(parent.word)
            if (
                self.get_part_of_speech(cur_node) == ["Прил"] or \
                self.get_part_of_speech(cur_node) == ["Сущв"]
            ):
                sentence.insert(i + 1, cur_node.word)

        # проверка на предлог -> сущв/мест
        if self.get_part_of_speech(parent) == ["Предлог"]:
            i = sentence.index(parent.word)
            if self.get_part_of_speech(cur_node) == ["Сущв"]:
                sentence.insert(i + 1, cur_node.word)

            if self.get_part_of_speech(cur_node) == ["Мест"]:
                sentence.insert(i + 1, cur_node.word)

        if not cur_node.child:
            return sentence

        #sentence += cur_node.word + " "
        for i, c in enumerate(cur_node.child):
            sentence = self.test_summarize(
                cur_node=c,
                sentence=sentence,
                depth=depth,
                parent=cur_node
            )
            if i == len(self.root.child) - 1:
                return sentence

        return sentence

    def while_test_summarize(
        self,
        sentence: str,
        depth: int
    ) -> str:
        prev: SentenceTreeNode
        cur: SentenceTreeNode = self.root
        while cur:
            if self.get_part_of_speech(cur) == []:
                if self.get_part_of_speech(cur.child[0]) == ["Сущв"]:
                    sentence += cur.child[0].word + " " + cur.word
                    prev = cur
                    cur = cur.child[0]
            if True:
                pass
            
