import csv

from Core.TuzovAnalyzer.addons import InfoProvider
from Core.TuzovAnalyzer.analyzer import Text, Expression, Sentence


class Dictionary:
    def __init__(self, dict_: dict, tagger: 'function') -> None:
        self.dict = dict_
        self.tagger = tagger
    
    def get_value(self, word: str) -> float:
        if word not in self.dict:
            return 0
        return self.dict[word]
    
    def get_tag(self, word: str) -> float:
        value = self.get_value(word)
        return self.tagger(value)


class SentimentRule:
    def __init__(self) -> None:
        super().__init__()
        
    def suitability(self, expression: Expression) -> float:
        return 0
    
    def apply(self, expression: Expression) -> float:
        return 0


def basic_tagger(value: float) -> str:
    if value < -1:
        return "NGTV"
    elif value > 1:
        return "PSTV"
    else:
        return "NEUT"


def load_dict(tagger_func: 'function'=basic_tagger) -> Dictionary:
    dict = {}
    
    dict_file = open(".\Core\TuzovAnalyzer\dict.csv", "r", encoding="utf-8")
    reader = csv.reader(dict_file, delimiter=";", dialect="unix")
    for row in reader:
        dict[row[0]] = float(row[2])
    
    return Dictionary(dict, tagger_func)


class SentimentProvider(InfoProvider):
    def __init__(self, dictionary: Dictionary=load_dict()) -> None:
        super().__init__()
        self.dictionary = dictionary
    
    def provide(self, words: list[str]) -> dict:
        score = 0
        for word in words:
            score += self.dictionary.get_value(word)
        
        tags = self.dictionary.get_tag(words[0])
        return {"sentiment_score": score, "sentiment_tag": tags}


class AddRule(SentimentRule):
    def suitability(self, expression: Expression) -> float:
        if "sentiment_result" in expression.added_tags:
            return -1
    
        for exp in expression.children:
            if "sentiment_result" not in exp.added_tags:
                return -1
        return 2
    
    def apply(self, expression: Expression) -> None:
        children_score = 0
        for child in expression.children:
            children_score += child.added_tags["sentiment_result"]
        
        expression.added_tags["sentiment_result"] = expression.added_tags["sentiment_score"] + children_score


class MultiplyRule(SentimentRule):
    def suitability(self, expression: Expression) -> float:
        if "sentiment_result" in expression.added_tags:
            return -1
        
        for exp in expression.children:
            if "sentiment_result" not in exp.added_tags:
                return -1
        return 2
    
    def apply(self, expression: Expression) -> None:
        children_score = 0
        for child in expression.children:
            children_score += child.added_tags["sentiment_result"]
        
        full_score = expression.added_tags["sentiment_score"] * children_score
        if full_score != 0:
            expression.added_tags["sentiment_result"] = full_score
        elif children_score != 0:
            expression.added_tags["sentiment_result"] = children_score
        else:
            expression.added_tags["sentiment_result"] = expression.added_tags["sentiment_score"]


class SentimentProcessor:
    def __init__(self, rules: list=None) -> None:
        super().__init__()
        if rules is None:
            rules = []
        self.rules = rules

    def get_score(self, text: Text) -> float:
        result = 0
        for sent in text.sentences:
            while "sentiment_result" not in sent.expression.added_tags:
                self._count_score(sent)
            sent_score = sent.expression.added_tags["sentiment_result"]
            print("sentence score: ", sent_score)
            result += sent_score
        print("final score: ", result)
        return result

    def classify(self, text: Text, classifier: 'function'):
        score = self.get_score(text)
        return classifier(score)

    def _count_score(self, sentence: Sentence):
        variants = []
        
        for rule in self.rules:
            for exp in sentence.word_expressions:
                variants.append([rule, exp, rule.suitability(exp)])
        variants = sorted(variants, key=lambda item: item[2], reverse=True)
        pair = variants[0]
        pair[0].apply(pair[1])
