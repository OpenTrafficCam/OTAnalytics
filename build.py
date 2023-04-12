import os
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile


def collect_files(
    base_path: Path,
    file_extension: str = ".py",
) -> list[Path]:
    """Collect all files in the file tree.

    Args:
        base_path (Path): base path to start searching files
        file_extension (str, optional): only files with this extension will be
            collected. Defaults to ".py".

    Returns:
        list[Path]: list of collected files.
    """
    paths: list[Path] = []
    for folder_name, subfolders, file_names in os.walk(base_path):
        for file_name in file_names:
            if file_name.endswith(file_extension):
                file_path = Path(folder_name, file_name)
                paths.append(file_path)
    return paths


def zip_output_folder(input_folder: Path, zip_file: Path) -> None:
    """Zip a whole directory into a zip file. The directory structure (subdirectories)
        will remain in the zip file.

    Args:
        input_folder (Path): folder to zip
        zip_file (Path): zipped folder as file
    """
    with ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as output:
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                file_path = Path(root, file)
                base_path = Path(input_folder, ".")
                output_path = file_path.relative_to(base_path)
                output.write(file_path, output_path)


def clean_directory(directory: Path) -> None:
    """Clean the given directory.

    Args:
        directory (Path): directory to clean.
    """
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(exist_ok=True)


@dataclass(frozen=True)
class Configuration:
    """Configuration for deployment. It contains all files required on the given
    platform (suffix)
    """

    _otanalytics_path: Path
    _files: list[Path]
    _additional_files: list[Path]
    _suffix: str

    def create_zip(
        self, file_name: str, output_directory: Path, temp_directory: Path
    ) -> None:
        """Create a zip file with the given name in the given output directory.
        Store temporal artifacts in the temp_folder.

        Args:
            file_name (str): name of the zip file.
            output_directory (Path): directory to store the zip file in.
            temp_directory (Path): directory for temporal artifacts.
        """
        clean_directory(build_path)
        zip_file = Path(output_directory, f"{file_name}-{self._suffix}.zip")
        self._copy_to_output_directory(temp_directory)
        zip_output_folder(temp_directory, zip_file)
        clean_directory(build_path)

    def _copy_to_output_directory(self, output_directory: Path) -> None:
        files = collect_files(base_path=self._otanalytics_path, file_extension=".py")
        self._copy_files(files, output_directory=output_directory)

        self._copy_files(self._files, output_directory=output_directory)
        self._copy_files(self._additional_files, output_directory=output_directory)

    def _copy_files(self, files: list[Path], output_directory: Path) -> None:
        """Copies all files into the output directory. The directory structure will
        remain.

        Args:
            files (list[Path]): files to copy.
            output_directory (Path): directory to copy the files to.
        """
        for file in files:
            output_file = Path(output_directory, file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(file, output_file)

    def _read_requirements(self, requirements_file: Path) -> str:
        """Read content of existing requirements file.

        Args:
            requirements_file (Path): path to requirements.txt

        Returns:
            str: content of requirements.txt
        """
        with open(requirements_file, "r") as requirements:
            return requirements.read()


build_path = Path("build")
distribution_path = Path("dist")
output_file_name = "otanalytics"

otanalytics_path = Path("OTAnalytics")

base_files = [
    Path("LICENSE"),
    Path("README.md"),
    Path("requirements.txt"),
]

windows_files = [
    Path("install.cmd"),
    Path("start_gui.cmd"),
]

unix_files = [
    Path("install.sh"),
    Path("start_gui.sh"),
]

configurations: list[Configuration] = [
    Configuration(
        _otanalytics_path=otanalytics_path,
        _files=base_files,
        _additional_files=windows_files,
        _suffix="win",
    ),
    Configuration(
        _otanalytics_path=otanalytics_path,
        _files=base_files,
        _additional_files=unix_files,
        _suffix="linux",
    ),
    Configuration(
        _otanalytics_path=otanalytics_path,
        _files=base_files,
        _additional_files=unix_files,
        _suffix="macOS",
    ),
]

clean_directory(distribution_path)
for configuration in configurations:
    configuration.create_zip(
        output_file_name,
        output_directory=distribution_path,
        temp_directory=build_path,
    )
