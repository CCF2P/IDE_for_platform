from Core.CoreController import CoreController


def run_module_by_name(name: str) -> None:
    cc = CoreController()
    cc.run_module(name)


def main():
    cc = CoreController()

    flag = True
    while flag:
        print("Меню")
        print("1 - Запустить анализатор Тузова")
        print("2 - Получить список модулей")
        print("3 - Получить список словарей")
        print("4 - Запустить модуль")
        print("5 - Выход")

        a: int = int(input("> "))
        if a == 1:
            print("Введите путь к входному файлу")
            path = input("> ")
            cc.run_analyzer(path)
        elif a == 2:
            print(cc.get_modules())
        elif a == 3:
            print(cc.get_dictionaries())
        elif a == 4:
            print("Введите название модуля")
            name = input("> ")
            run_module_by_name(name)
        elif a == 5:
            flag = False


main()
