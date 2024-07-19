
from TuzovAnalyzer.main import TuzovAnalyzer
from Summarize_.main import main
def start():
    with open(
        file="C:/Users/zhora/Desktop/Python/VKR_Platform/Core/output.txt",
        mode="w"
    ) as output:
        res = main(tanalyzer=TuzovAnalyzer())
        if isinstance(res, list):
            for i in res:
                output.write(i)
        elif isinstance(res, str):
            output.write(res)
start()
                            