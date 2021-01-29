from io import StringIO

from .output import Output
from .section_output import SectionOutput


class BufferedOutput(Output):
    def __init__(self, decorated: bool = False, supports_utf8: bool = True) -> None:
        super().__init__(decorated=decorated)

        self._buffer = StringIO()
        self._supports_utf8 = supports_utf8

    def fetch(self) -> str:
        """
        Empties the buffer and returns its content.
        """
        content = self._buffer.getvalue()
        self._buffer = StringIO()

        return content

    def clear(self) -> None:
        """
        Empties the buffer.
        """
        self._buffer = StringIO()

    def supports_utf8(self) -> bool:
        return self._supports_utf8

    def set_supports_utf8(self, supports_utf8: bool) -> None:
        self._supports_utf8 = supports_utf8

    def section(self) -> SectionOutput:
        return SectionOutput(
            self._buffer,
            self._section_outputs,
            verbosity=self.verbosity,
            decorated=self.is_decorated(),
            formatter=self.formatter,
        )

    def _write(self, message: str, new_line: bool = False) -> None:
        self._buffer.write(message)

        if new_line:
            self._buffer.write("\n")
