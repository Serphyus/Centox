from typing import Any, Callable, Sequence


class Section:
    def __init__(self,
            contents: Sequence[Any],
            callback: Callable,
            *args
        ) -> None:
        
        self._paddings = [*map(lambda s: len(str(s)), contents)]

        for index, value in enumerate(contents):
            if isinstance(value, bool):
                color = '92' if value else '91'
                value = '\033[%sm%s\033[0m' % (color, value)
            
            contents[index] = value

        self._contents = contents
        self._callback = callback
        self._args = args
    

    @property
    def contents(self) -> Sequence[str]:
        return self._contents


    @property
    def paddings(self) -> Sequence[int]:
        return self._paddings


    def get_item(self, index: str) -> str:
        return self._contents[index]
    

    def set_item(self, index: str, value: str) -> None:
        self._contents[index] = value


    def call(self) -> Any:
        return self._callback(*self._args)