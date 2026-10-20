from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExportFileDto:
    """
    Data transfer object for file export information.

    Attributes:
        export_directory (Path): The directory where the file will be exported.
        file_stem (str): The stem of the file name (without extension).
        export_format (str): The format of the exported file. The file extension.
    """

    export_directory: Path
    file_stem: str
    export_format_extension: str
    export_format: str

    @classmethod
    def from_file_path(cls, file_path: Path, export_format: str) -> "ExportFileDto":
        return cls(
            export_directory=file_path.parent,
            file_stem=file_path.stem,
            export_format_extension=file_path.suffix,
            export_format=export_format,
        )

    def as_file_path(self) -> Path:
        return self.export_directory / f"{self.file_stem}{self.export_format_extension}"
