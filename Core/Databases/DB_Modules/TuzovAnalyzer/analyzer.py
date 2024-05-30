import os
import re

from .addons import InfoProvider
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    Doc
)

morph_vocab = MorphVocab()
segmenter = Segmenter()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)


class Expression:
    def __init__(self, exp_str, children) -> None:
        self.connection = ''
        self.code = ''
        self.properties = []
        self.raw_words = ''
        self.words = []
        self._parse(exp_str)
        self.exp_str = exp_str
        self.children = children
        self.added_tags = {}
    
    def _parse(self, exp_str: str) -> None:
        result = re.search(r"(?<=@)(\w+)", exp_str)
        if result is not None:
            self.connection = result.group(0)
        
        self._extract_properties(exp_str)
        
        # self.raw_words = re.search(r"(?<=\s)([^<])+(?=<)", text).group(0)
        self.raw_words = re.search(r"([^<| ])+(?=<)", exp_str).group(0)
        
        self.words = self.get_lemmas(self.raw_words)
        # print("words: ", self.words)
    
    def _extract_properties(self, exp_str: str) -> None:
        in_prop = False
        prop = ''
        for char in exp_str:
            if char == "<":
                in_prop = True
            
            if in_prop:
                prop += char
            
            if char == ">":
                self.properties.append(prop)
                in_prop = False
                prop = ''
    
    @staticmethod
    def get_lemmas(text: str) -> list:
        doc = Doc(text.replace("_", " "))
        
        doc.segment(segmenter)
        doc.tag_morph(morph_tagger)
        
        for token in doc.tokens:
            token.lemmatize(morph_vocab)
        
        lemmas = []
        for token in doc.tokens:
            lemmas.append(token.lemma)
        
        return lemmas


class Sentence:
    def __init__(self, sentence_data: str, word_descriptions: str) -> None:
        parts = sentence_data.split("......................................................\n")
        # parts[0] is a text with a whitespace at the beginning and newline at the end
        self.text = parts[0][1:-1]
        self.tree_str = parts[1]
        # retrieving sentences of analyzed text
        # in form of parse tree
        self.expression = self._extract_expressions(self.tree_str)[0]
        self._extract_words(word_descriptions)
        self.word_expressions = []
        self._create_expression_list(self.expression)
    
    def _create_expression_list(self, root) -> None:
        self.word_expressions.append(root)
        for exp in root.children:
            self._create_expression_list(exp)
    
    def _extract_words(self, word_descriptions: str) -> None:
        words = []
        lines = word_descriptions[:-1].split("\n")
        word = [lines[0]]
        for line in lines[1:]:
            if len(line) == 0:
                break
            if line[0] != " ":
                words.append(word)
                word = []
            word.append(line)
        words.append(word)
        self._add_word_desc_to_tree(self.expression, words)
    
    def _add_word_desc_to_tree(self, root, words) -> None:
        for word in words:
            if word[0] == root.raw_words:
                for i in range(2, len(word)):
                    root.properties.append(word[i])
                break
        for child in root.children:
            self._add_word_desc_to_tree(child, words)
    
    # recursively creates tree of expressions from the AWAT function
    def _extract_expressions(self, awat_func: str) -> list:
        working = True
        data = awat_func
        
        expressions = []
        
        while working:
            name_data = self._find_name(data)
            
            # if there is no name, then it's the end of the data
            if name_data is None:
                working = False
            else:
                data = self._remove_unnecessary_symbols(data[name_data[1]:])
                args_data = self._find_args(data)
                data = self._remove_unnecessary_symbols(data[args_data[1]:])
                # print("word: ", name_data[0], "\nargs: \n", args_data[0])
                # add word to the list with args as children, search in args recursively
                exp = Expression(name_data[0], self._extract_expressions(args_data[0]))
                expressions.append(exp)
        
        return expressions
    
    # uses regexp to retrieve the name of the function from the start of the string
    @staticmethod
    def _find_name(data: str) -> list:
        result = re.match(r"((.)+)>", data)
        if result is None:
            return None
        return [result.group(0), result.end()]
    
    # loops through nested brackets and retrieves all the data inside of this construction
    @staticmethod
    def _find_args(data: str) -> list:
        if len(data) == 0:
            return ["", 0]
        
        counter = 0
        pos = 0
        search = True
        
        while search:
            if data[pos] == '(':
                counter += 1
            elif data[pos] == ')':
                counter -= 1
            
            if counter == 0:
                search = False
            else:
                pos += 1
        
        params = data[1:pos]
        return [params, pos]
    
    # removes ")", "," and whitespaces from the start of the string
    @staticmethod
    def _remove_unnecessary_symbols(data: str) -> str:
        return data[re.match(r"\)*,*\s*", data).end():]
    
    def add_info_from(self, provider: InfoProvider) -> None:
        for exp in self.word_expressions:
            tags = provider.provide(exp.words)
            for key in tags:
                if key not in exp.added_tags:
                    exp.added_tags[key] = tags[key]


class Text:
    def __init__(self, analyzed_text: str, providers: list=None) -> None:
        if providers is None:
            providers = []
        self.sentences = []
        self.analyzer_report = analyzed_text
        # extracting grammar from A-WAT's result
        tree_data = analyzed_text.split(
            "......................................................\n"
        )[1].split(
            "======================================================"
        )[0]
        # split awat output by "magic" string,
        # that's placed after each part of the output
        # produces sequence which consists of sentence trees and
        # word descriptions corresponding to this trees
        analyzed_parts = analyzed_text.split(
            "======================================================\n"
        )
        # remove header
        analyzed_parts.pop(0)
        for i in range(len(analyzed_parts) // 2):
            self.sentences.append(
                Sentence(analyzed_parts[i * 2], analyzed_parts[i * 2 + 1])
            )
        # print(tree_data)
        
        # adding provider info to sentences
        if providers != []:
            for sentence in self.sentences:
                for provider in providers:
                    sentence.add_info_from(provider)


class Analyzer:
    def __init__(self, providers: list=None) -> None:
        if providers is None:
            providers = []
        self.providers = providers
    
    # send data to A-WAT analyser, execute it and get result
    def analyse(self, data: str) -> Text:
        res = data
        res = re.sub(r"[А-ЯЁа-яё]", "", res)

        res = re.sub(r"\W", "", res)
        if len(res) != 0:
            raise UnexpectedCharactersError()
        
        # if len(data) > 140:
            # raise TextIsTooLongError()
        
        res = re.search(r"^[А-ЯЁ]", data)
        if res is None:
            raise NoFirstCapitalLetter()
        
        # Проверяем, что в data находится предложение
        res = re.findall(r"[.!?]", data)
        if len(res) == 0:
            raise UnableToDetectSentenceError()
        #elif len(res) > 5:
        #    raise TooManySentencesError()

        # Ищем окончание предложения - .!?
        if (data[-1] != ".") and (data[-1] != "?") and (data[-1] != "!"):
            raise NoLastSignError()

        self._push_input(data)
        self._execute_awat()
        analyzed_text = self._get_output()

        text = Text(analyzed_text, self.providers)
        #text = Text(analyzed_text=analyzed_text)
        return text

    # write data to A-WAT input file
    @staticmethod
    def _push_input(data: str) -> None:
        analiz_file = open("c:\\analiz\\infile.txt", "wb")
        analiz_file.write(data.encode("windows-1251"))
        analiz_file.close()

    # execute A-WAT through command line
    @staticmethod
    def _execute_awat() -> None:
        os.system("c:\\analiz\\WORK\\SEMLPB.exe zt fw04.03")

    # read results of A-WAT
    @staticmethod
    def _get_output() -> None:
        awat_file = open("c:\\analiz\\result.txt", "r")
        data = awat_file.read()
        awat_file.close()
        return data


class UnexpectedCharactersError(Exception):
    pass


class TextIsTooLongError(Exception):
    pass


class NoFirstCapitalLetter(Exception):
    pass


class UnableToDetectSentenceError(Exception):
    pass


class TooManySentencesError(Exception):
    pass


class NoLastSignError(Exception):
    pass
