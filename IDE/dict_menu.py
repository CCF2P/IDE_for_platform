import re
import os.path
import subprocess
import csv

from textual.app import App, ComposeResult, on
from textual.binding import Binding
from textual.screen import Screen, ModalScreen
from textual.containers import (
    Grid,
    Container,
    Horizontal
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


class DictList(Screen):
    DICT_LIST: list[str]

    CSS_PATH = "./dict_list.tcss"
    BINDINGS = [
        Binding("escape", "exit", "Close dictionaries list", show=False, priority=True)
    ]

    def __init__(self, core_controller) -> None:
        super().__init__()
        self.core_controller = core_controller
        self.DICT_LIST = self.core_controller.get_dictionaries()

    def compose(self) -> ComposeResult:
        yield Footer()
        with Grid(id="dict_wnd"):
            with Container(id="dict_list_view"):
                yield Label(
                    renderable="DICTIONARIES",
                    id="DICTIONARIES"
                )
                yield ListView(
                    id="list_of_dict"
                )

            yield DataTable(id="dict_content_table")

            with Container(id="option_dict_menu"):
                with Horizontal(id="panel_dict_button"):
                    yield Button(
                        label="Start",
                        id="btn_to_start_dict"
                    )
                    yield Button(
                        label="Prev page",
                        id="btn_prev_page_dict"
                    )
                    yield Button(
                        label="Next page",
                        id="btn_next_page_dict"
                    )
                    yield Button(
                        label="End",
                        id="btn_to_end_dict"
                    )
                yield Log(highlight=True)
    
    def action_exit(self) -> None:
        self.app.pop_screen()

    def _load_dict_to_datatable(self, file_name: str) -> None:
        with open(
            file=f"./Core/Databases/DB_Dictionaries/{file_name}",
            mode="r",
            encoding="utf8"
        ) as csv_dict:
            spamreader = csv.reader(
                csv_dict,
                delimiter=';',
                quotechar='|'
            )

            datatable: DataTable = self.query_one("#dict_content_table")
            datatable.clear(columns=True)

            flag = True
            number = 1
            for row in spamreader:
                if number == 1001:
                    break
                if flag:
                    count_columns = len(row)
                    for i in range(count_columns):
                        datatable.add_column(" ")
                    flag = False
                datatable.add_row(*row, label=number)
                number += 1

    @on(message_type=ListView.Selected, selector="#list_of_dict")
    def list_of_dict_select(self, event: ListView.Selected) -> None:
        log = self.query_one(Log)
        log.write(event.item.name)
        self._load_dict_to_datatable(event.item.name)

    @on(message_type=Button.Pressed)
    def button_pressed(self, event: Button.Pressed) -> None:
        log = self.query_one(Log)
        if event.button.id == "btn_to_start_dict":
            log.write_line("btn_to_start_dict")
        elif event.button.id == "btn_prev_page_dict":
            log.write_line("btn_prev_page_dict")
        elif event.button.id == "btn_next_page_dict":
            log.write_line("btn_next_page_dict")
        elif event.button.id == "btn_to_end_dict":
            log.write_line("btn_to_end_dict")

    def on_mount(self) -> None:
        dict_list: ListView = self.query_one("#list_of_dict")
        for name in self.DICT_LIST:
            item = ListItem(
                Label(renderable=name),
                name=name
            )
            dict_list.append(item)

        table = self.query_one(DataTable)
        table.cursor_type = "row"