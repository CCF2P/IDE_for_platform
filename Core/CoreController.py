import sys
import subprocess

from Core.Databases.DatabaseController import DatabaseController
from Core.Databases.DB_Modules.TuzovAnalyzer.main import main


class CoreController():
    def __init__(self) -> None:
        self._db_controller = DatabaseController()
        
    def run_analyzer(self, path: str=None):
        if path is None:
            return main()
        return main(path)

    def _update_dict_list(self) -> None:
        self._db_controller._update_dict_list()

    def _update_modules_list(self) -> None:
        self._db_controller._update_modules_list()

    def get_modules(self) -> list[str]:
        return self._db_controller.get_modules()
    
    def get_dictionaries(self) -> list[str]:
        return self._db_controller.get_dictionaries()
    
    def run_module(self, name: str) -> None:
        mod_path = self._db_controller.get_module_path(name)
        if mod_path == "None":
            return
        
        subprocess.run(
            args=[
                sys.executable,
                mod_path,
            ]
        )

