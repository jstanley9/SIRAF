import io
import pathlib
import config


class raFile(io.BytesIO):
    __SUFFIX = ".ravrf"
    __DOT = "."

    def __init__(self, path: pathlib.Path = None):
        self.__path: pathlib.Path = None
        self.__config: config.RavrfConfig = None
        self.__size: int = 0

        if path:
            self.setPath(path)

    def setPath(self, path: pathlib.Path):
        if path.name.beginswith(self.__DOT):
            raise ValueError("File name cannot start with a dot")
        
        suffix = path.suffix.lower()
        if len(suffix) == 0:
            self.__path = path.with_suffix(self.__SUFFIX)
        else:
            if suffix != self.__SUFFIX:
                raise ValueError(f"File suffix must be '{self.__SUFFIX}' or None")
            self.__path = path

        if self.__path.exists():
            if not self.__path.is_file():
                raise IsADirectoryError(f"Path '{self.__path}' is not a file")
            self.__size = self.__path.stat().st_size
