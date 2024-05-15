from Core.TuzovAnalyzer.analyzer import Analyzer, Expression
from Core.TuzovAnalyzer.sentiment import SentimentProvider


def get_input() -> str:
    input_file = open("./Core/TuzovAnalyzer/input.txt", "rb")
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

if __name__ == "__main__":
    main()
