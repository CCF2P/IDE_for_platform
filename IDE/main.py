import re
import os.path
import subprocess
import shutil

from textual.app import App, ComposeResult, on
from textual.binding import Binding
from textual.screen import Screen, ModalScreen
from textual.containers import (
    Grid,
    Container,
    Horizontal,
    Vertical,
    Center
)
from textual.widgets import (
    Header,
    Footer,
    Button,
    Label,
    DirectoryTree,
    TextArea,
    Static,
    Log,
    Input,
    TabbedContent,
    TabPane,
    ListView,
    ListItem,
    DataTable
)

from IDE.dict_menu import DictList


_PATH_TO_INPUT_FILE: str = "C:/Users/zhora/Desktop/Python/VKR_Platform/Core/TuzovAnalyzer/input.txt"


class AddModule(ModalScreen):
    def __init__(self) -> None:
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Grid(
            Input(
                placeholder="Enter the path to the directory",
                type="text",
                id="input_path_module"
            ),
            Button(
                "Add",
                variant="primary",
                id="btn_add",
                classes="folder_path_btn"
            ),
            Button(
                "Cancel",
                variant="error",
                id="btn_cancel",
                classes="folder_path_btn"
            ),
            id="folder_path_dialog"
        )

    def _clear_input(self) -> None:
        inp: Input = self.query_one("#input_path_module")
        inp.clear()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_add":
            path: str = self.query_one(Input).value
            
            if os.path.isdir(path):
                if not os.path.isfile(path + "/main.py"):
                    self.app.push_screen(InfoWindow("Script 'main.py' does not exist"))
                    self._clear_input()
                else:
                    module_path_info: list[str] = path.split("/")
                    module_name: str = module_path_info[len(module_path_info) - 1]
                    try:
                        # Create folder for new module
                        os.mkdir(
                            path="C:/Users/zhora/Desktop/Python/VKR_Platform/Core/Databases/DB_Modules/" + module_name + "_"
                        )
                        # Copy new module in new folder
                        shutil.copytree(
                            src=path,
                            dst="C:/Users/zhora/Desktop/Python/VKR_Platform/Core/Databases/DB_Modules/" + module_name + "_",
                            dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("venv", ".venv")
                        )

                        # if exist folder ".venv" or "venv", we need to remove it
                        #if os.path.isdir("C:/Users/zhora/Desktop/Python/VKR_Platform/Core/Databases/DB_Modules/" + module_name + "_" + "/venv"):
                        #    os.remove("C:/Users/zhora/Desktop/Python/VKR_Platform/Core/Databases/DB_Modules/" + module_name + "_" + "/venv")
                        #elif os.path.isdir("C:/Users/zhora/Desktop/Python/VKR_Platform/Core/Databases/DB_Modules/" + module_name + "_" + "/.venv"):
                        #    os.remove.isdir("C:/Users/zhora/Desktop/Python/VKR_Platform/Core/Databases/DB_Modules/" + module_name + "_" + "/.venv")

                        # create init script for new module, that we will see in list of modules in user mode
                        with open(
                            file="C:/Users/zhora/Desktop/Python/VKR_Platform/Core/Databases/DB_Modules/" +
                            module_name +
                            ".py",
                            mode="w"
                        ) as init_script:
                            init_script.write(f"""
from TuzovAnalyzer.main import TuzovAnalyzer
from {module_name}_.main import main
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
                            """)
                    except FileExistsError as e:
                        self.app.push_screen(InfoWindow(f"{e}"))
                        self._clear_input()
                        return
                    except BaseException as e:
                        self.app.push_screen(InfoWindow(f"{e}"))
                        self._clear_input()
                        return
                    
                    self.app.push_screen(InfoWindow("Module has been successfully added"))
                    self._clear_input()
            else:
                self.app.push_screen(InfoWindow("Invalid path to folder with module"))
                self._clear_input()
        elif event.button.id == "btn_cancel":
            self.app.pop_screen()


class MainMenu(ModalScreen):
    def __init__(self, core_controller) -> None:
        super().__init__()
        self.core_controller = core_controller
    
    def compose(self) -> ComposeResult:
        with Vertical(id="main_menu_dialog"):
            with Center():
                yield Button(
                    label="Add module",
                    variant="primary",
                    id="btn_add_module"
                )
            with Center():
                yield Button(
                    label="Open dictionary menu",
                    variant="primary",
                    id="btn_open_dict_menu"
                )
            with Center():
                yield Button(
                    label="Close",
                    variant="error",
                    id="btn_close_main_menu"
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_close_main_menu":
            self.app.pop_screen()
        elif event.button.id == "btn_add_module":
            self.app.pop_screen()
            self.app.push_screen(AddModule())
        elif event.button.id == "btn_open_dict_menu":
            self.app.pop_screen()
            self.app.push_screen(DictList(self.core_controller))


class InfoWindow(ModalScreen):
    def __init__(self, msg: str) -> None:
        super().__init__()
        self.msg = msg
    
    def compose(self) -> ComposeResult:
        yield Grid(
            Label(
                self.msg,
                id="msg_info"
            ),
            Button(
                "Ok",
                variant="primary",
                id="btn_confirm",
                classes="folder_path_btn"
            ),
            id="info_msg_dialog"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_confirm":
            self.app.pop_screen()


class OpenFolder(ModalScreen):
    def __init__(self, dt: DirectoryTree) -> None:
        super().__init__()
        self.dt = dt

    def compose(self) -> ComposeResult:
        yield Grid(
            Input(
                placeholder="Enter the path to the directory",
                type="text",
                id="input_path_folder"
            ),
            Button(
                "Open",
                variant="primary",
                id="btn_open",
                classes="folder_path_btn"
            ),
            Button(
                "Cancel",
                variant="error",
                id="btn_cancel",
                classes="folder_path_btn"
            ),
            id="folder_path_dialog"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_open":
            path = self.query_one(Input).value
            
            if os.path.isdir(path):
                self.dt.path = path
                self.dt.reload()
                self.app.pop_screen()
            else:
                self.app.push_screen(InfoWindow("Invalid path to folder"))
                inp: Input = self.query_one("#input_path_folder")
                inp.clear()
                # self.app.pop_screen()
        elif event.button.id == "btn_cancel":
            self.app.pop_screen()


class MainWindow(App):
    CSS_PATH = "./main.tcss"
    BINDINGS = [
        Binding("ctrl+o", "open_folder", "Open folder", show=True, priority=True),
        Binding("ctrl+s", "save_file", "Save file", show=True, priority=True),
        Binding("ctrl+k", "close_current_tab", "Close tab", show=True, priority=True),
        Binding("ctrl+b", "open_menu", "Menu", show=True, priority=True)
    ]

    def __init__(self, core_controller) -> None:
        super().__init__()
        self.title = "IDE"
        self.file_content = Static(expand=True)
        self.core_controller = core_controller

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Grid():
            yield Container(
                Label("EXPLORER"),
                DirectoryTree("./"),
                id="DirTree"
            )
            yield TabbedContent(id="FilesTab")
            yield Container(
                Label("Console"),
                Log(highlight=True),
                Input(id="ConsoleInput"),
                id="OutputMenu"
            )

    def action_close(self) -> None:
        self.exit()
    
    def action_open_menu(self) -> None:
        self.push_screen(MainMenu(self.core_controller))

    def action_close_current_tab(self) -> None:
        tabbed_cnt: TabbedContent = self.query_one("#FilesTab")
        if tabbed_cnt.active_pane == None:
            return
        tabbed_cnt.remove_pane(tabbed_cnt.active_pane.id)
    
    def action_open_folder(self) -> None:
        dt = self.query_one(DirectoryTree)
        self.push_screen(OpenFolder(
            dt=dt
        ))

    def action_save_file(self) -> None:
        log = self.query_one(Log)
        file: DirectoryTree = self.query_one(DirectoryTree)
        cur_tab: TabbedContent = self.query_one("#FilesTab")

        if cur_tab.active_pane == None:
            return
        
        try:
            with open(
                file.path.__str__() + "\\" + cur_tab.active_pane.children[0].name.__str__(),
                "w"
            ) as file:
                file.write(cur_tab.active_pane.children[0].text.__str__())
        except Exception as e:
            log.write_line(e.__str__())
            self.push_screen(InfoWindow("Error saving the file"))
            return

        self.push_screen(InfoWindow("The file was saved successfully"))
    
    @on(message_type=Input.Submitted, selector="#ConsoleInput")
    def action_consloe_input(self) -> None:
        log: Log = self.query_one(Log)
        input: Input = self.query_one("#ConsoleInput")
        dt: DirectoryTree = self.query_one(DirectoryTree)
        
        cmd = input.value.split(sep=" ")
        if cmd[0] == "cls":
            log.clear()
        else:
            try:
                output = subprocess.check_output(
                    cmd,
                    shell=True
                ).decode("cp866")
                log.write_line(output)
            except Exception as e:
                log.write_line(e.__str__())
        input.clear()
        dt.reload()


    def on_directory_tree_file_selected(self, message: DirectoryTree.FileSelected) -> None:
        log = self.query_one(Log)
        #log.write("path - " + message.path.__str__())

        try:
            #log.write_line("read text")
            file_content = message.path.read_text()
        except UnicodeDecodeError as e:
            log.write_line("error")
            log.write_line(e.reason)
            self.file_content.update("")
            return None

        #lexer: str = Syntax.guess_lexer(path=message.path.name, code=file_content)
        #data = Syntax(code=file_content, lexer=lexer)
        #self.file_content.update(data)

        file_name: str = re.findall(r"(\w+[.]\w+)", message.path.as_posix())[0]
        file: list = file_name.split(".")
        fn: str = file[0]
        ft: str = file[1]
        #log.write_line("check tab")

        # Проверка на то, чтобы не открывать один файл дважды
        tabbed_cnt: TabbedContent = self.query_one("#FilesTab")
        for i in tabbed_cnt.children:
            for j in i.children:
                if j.id == fn + ft:
                    return

        if ft == "py":
            lng = "python"
        else:
            lng = None
        #log.write(ft)
        ntab_pane = TabPane(title=file_name, id=f"{fn + ft}")
        #log.write_line("create tab")
        ntab_pane.compose_add_child(
            TextArea.code_editor(
                text=file_content,
                language=lng,
                id=f"{fn + ft}",
                name=message.path.__str__()
            )
        )
        #log.write_line("fill tab")

        tabcnt = self.query_one("#FilesTab")
        tabcnt.add_pane(ntab_pane)


def run_ide(core_controller):
    app = MainWindow(core_controller=core_controller)
    app.run()
