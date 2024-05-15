import os

_PATH_TO_MODULES: str = os.path.curdir + "/Core/Databases/DB_Modules/"
_PATH_TO_DICTIONARIES: str = os.path.curdir + "/Core/Databases/DB_Dictionaries/"


class DatabaseController():
    MODULES: list[str]
    DICTIONARRIES: list[str]

    def __init__(self) -> None:
        self.MODULES = list()
        self.DICTIONARRIES = list()

        self._update_modules_list()
        self._update_dict_list()

    def _update_dict_list(self) -> None:
        self.DICTIONARRIES.clear()
        for file in os.listdir(_PATH_TO_DICTIONARIES):
            if os.path.isfile(os.path.join(_PATH_TO_DICTIONARIES, file)):
                self.DICTIONARRIES.append(file)

    def _update_modules_list(self) -> None:
        self.MODULES.clear()
        for file in os.listdir(_PATH_TO_MODULES):
            if os.path.isfile(os.path.join(_PATH_TO_MODULES, file)):
                self.MODULES.append(file)

    def get_modules(self) -> list[str]:
        return self.MODULES
    
    def get_dictionaries(self) -> list[str]:
        return self.DICTIONARRIES
    
    def get_module_path(self, name: str) -> str:
        for i in self.MODULES:
            if i == name + ".py":
                return _PATH_TO_MODULES + name + ".py"
        return "None"
