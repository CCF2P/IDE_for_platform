from TestModule_.main import main

def start():
    with open(
        file="C:/Users/zhora/Desktop/Python/VKR_Platform/Core/output.txt",
        mode="w"
    ) as output:
        output.write(main())

start()