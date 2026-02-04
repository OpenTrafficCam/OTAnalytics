#!/usr/bin/env python3
"""
Clean Architecture Import Checker for OTCloud

This script validates that the OTCloud project follows Clean Architecture import
rules. The architecture has 5 layers:
1. abstraction (innermost layer)
2. domain
3. application
4. adapter_*
5. plugin_* (outermost layer)

Import Rules:
- Modules can only import from the same layer or inner (more central) layers
- Abstraction can only import from abstraction and standard libraries
- Domain can only import from abstraction, domain, and standard libraries
- Application can import from abstraction, domain, application, and standard libraries
- Adapter can import from abstraction, domain, application, adapter, and std libraries
- Plugin can import from all layers, standard libraries, and external libraries
- External library dependencies (non-stdlib) are only allowed in the plugin layer
- NO imports from outer layers to inner layers are allowed

Usage:
    python check_clean_architecture.py [--path PATH] [--verbose]
"""

import ast
import os
import sys
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Tuple

# Constants for architectural layers and project configuration
PROJECT_NAME = "OTCloud"
LAYER_ABSTRACTION = "abstraction"
LAYER_DOMAIN = "domain"
LAYER_APPLICATION = "application"
LAYER_ADAPTER_PREFIX = "adapter_"
LAYER_PLUGIN_PREFIX = "plugin_"
LAYER_HELPERS = "helpers"

# Standard library modules (Python 3.x)
STDLIB_MODULES = frozenset(
    {
        "abc",
        "aifc",
        "argparse",
        "array",
        "ast",
        "asynchat",
        "asyncio",
        "asyncore",
        "atexit",
        "audioop",
        "base64",
        "bdb",
        "binascii",
        "binhex",
        "bisect",
        "builtins",
        "bz2",
        "calendar",
        "cgi",
        "cgitb",
        "chunk",
        "cmath",
        "cmd",
        "code",
        "codecs",
        "codeop",
        "collections",
        "colorsys",
        "compileall",
        "concurrent",
        "configparser",
        "contextlib",
        "contextvars",
        "copy",
        "copyreg",
        "cProfile",
        "crypt",
        "csv",
        "ctypes",
        "curses",
        "dataclasses",
        "datetime",
        "dbm",
        "decimal",
        "difflib",
        "dis",
        "distutils",
        "doctest",
        "email",
        "encodings",
        "enum",
        "errno",
        "faulthandler",
        "fcntl",
        "filecmp",
        "fileinput",
        "fnmatch",
        "formatter",
        "fractions",
        "ftplib",
        "functools",
        "gc",
        "getopt",
        "getpass",
        "gettext",
        "glob",
        "graphlib",
        "grp",
        "gzip",
        "hashlib",
        "heapq",
        "hmac",
        "html",
        "http",
        "idlelib",
        "imaplib",
        "imghdr",
        "imp",
        "importlib",
        "inspect",
        "io",
        "ipaddress",
        "itertools",
        "json",
        "keyword",
        "lib2to3",
        "linecache",
        "locale",
        "logging",
        "lzma",
        "mailbox",
        "mailcap",
        "marshal",
        "math",
        "mimetypes",
        "mmap",
        "modulefinder",
        "multiprocessing",
        "netrc",
        "nis",
        "nntplib",
        "numbers",
        "operator",
        "optparse",
        "os",
        "ossaudiodev",
        "parser",
        "pathlib",
        "pdb",
        "pickle",
        "pickletools",
        "pipes",
        "pkgutil",
        "platform",
        "plistlib",
        "poplib",
        "posix",
        "posixpath",
        "pprint",
        "profile",
        "pstats",
        "pty",
        "pwd",
        "py_compile",
        "pyclbr",
        "pydoc",
        "queue",
        "quopri",
        "random",
        "re",
        "readline",
        "reprlib",
        "resource",
        "rlcompleter",
        "runpy",
        "sched",
        "secrets",
        "select",
        "selectors",
        "shelve",
        "shlex",
        "shutil",
        "signal",
        "site",
        "smtpd",
        "smtplib",
        "sndhdr",
        "socket",
        "socketserver",
        "spwd",
        "sqlite3",
        "ssl",
        "stat",
        "statistics",
        "string",
        "stringprep",
        "struct",
        "subprocess",
        "sunau",
        "symbol",
        "symtable",
        "sys",
        "sysconfig",
        "syslog",
        "tabnanny",
        "tarfile",
        "telnetlib",
        "tempfile",
        "termios",
        "test",
        "textwrap",
        "threading",
        "time",
        "timeit",
        "tkinter",
        "token",
        "tokenize",
        "tomllib",
        "trace",
        "traceback",
        "tracemalloc",
        "tty",
        "turtle",
        "turtledemo",
        "types",
        "typing",
        "unicodedata",
        "unittest",
        "urllib",
        "uu",
        "uuid",
        "venv",
        "warnings",
        "wave",
        "weakref",
        "webbrowser",
        "winreg",
        "winsound",
        "wsgiref",
        "xdrlib",
        "xml",
        "xmlrpc",
        "zipapp",
        "zipfile",
        "zipimport",
        "zlib",
        "zoneinfo",
        "__future__",
        "__main__",
        "_thread",
    }
)


class ArchitecturalLayer(Enum):
    """Defines the architectural layers in order from innermost to outermost"""

    ABSTRACTION = auto()
    DOMAIN = auto()
    APPLICATION = auto()
    ADAPTER = auto()
    PLUGIN = auto()
    HELPERS = auto()  # Utility layer
    EXTERNAL = auto()  # Standard library and third-party


@dataclass
class ImportViolation:
    """Represents a Clean Architecture import violation"""

    file_path: str
    line_number: int
    imported_module: str
    violating_import: str
    source_layer: ArchitecturalLayer
    target_layer: ArchitecturalLayer
    reason: str


class CleanArchitectureChecker:
    def __init__(self, project_root: str = PROJECT_NAME):
        self.project_root = Path(project_root)
        self.violations: List[ImportViolation] = []

        # Define layer hierarchy (inner to outer)
        self.layer_hierarchy = [
            ArchitecturalLayer.ABSTRACTION,
            ArchitecturalLayer.DOMAIN,
            ArchitecturalLayer.APPLICATION,
            ArchitecturalLayer.ADAPTER,
            ArchitecturalLayer.PLUGIN,
            ArchitecturalLayer.HELPERS,
        ]

        # Standard library modules (Python 3.x)
        self.stdlib_modules = STDLIB_MODULES

    def is_external_library(self, module_name: str) -> bool:
        """Check if a module is an external (third-party) library"""
        if module_name == PROJECT_NAME or module_name.startswith(f"{PROJECT_NAME}."):
            return False

        # Get the top-level module name
        top_level = module_name.split(".")[0]

        # Check if it's a standard library module
        if top_level in self.stdlib_modules:
            return False

        # It's an external library
        return True

    def categorize_module_layer(self, module_name: str) -> ArchitecturalLayer:
        """Determine which architectural layer a module belongs to"""
        if not module_name.startswith(f"{PROJECT_NAME}."):
            return ArchitecturalLayer.EXTERNAL

        parts = module_name.split(".")
        if len(parts) < 2:
            return ArchitecturalLayer.EXTERNAL

        layer_part = parts[1]  # OTCloud.<layer_part>

        if layer_part == LAYER_ABSTRACTION:
            return ArchitecturalLayer.ABSTRACTION
        elif layer_part == LAYER_DOMAIN:
            return ArchitecturalLayer.DOMAIN
        elif layer_part == LAYER_APPLICATION:
            return ArchitecturalLayer.APPLICATION
        elif layer_part.startswith(LAYER_ADAPTER_PREFIX):
            return ArchitecturalLayer.ADAPTER
        elif layer_part.startswith(LAYER_PLUGIN_PREFIX):
            return ArchitecturalLayer.PLUGIN
        elif layer_part == LAYER_HELPERS:
            return ArchitecturalLayer.HELPERS
        else:
            # Unknown OTCloud module, treat as external
            return ArchitecturalLayer.EXTERNAL

    def is_import_allowed(
        self,
        source_layer: ArchitecturalLayer,
        target_layer: ArchitecturalLayer,
        imported_module: str,
    ) -> bool:
        """Check if importing from target_layer to source_layer is allowed"""
        if target_layer == ArchitecturalLayer.EXTERNAL:
            # Check if it's an external library (non-stdlib)
            if self.is_external_library(imported_module):
                # External libraries are only allowed in plugin layer
                return source_layer == ArchitecturalLayer.PLUGIN
            # Standard library is allowed in all layers
            return True

        if target_layer == ArchitecturalLayer.HELPERS:
            return True  # All layers can import from helpers (utility layer)

        if source_layer == target_layer:
            return True  # Same layer imports are allowed

        try:
            source_index = self.layer_hierarchy.index(source_layer)
            target_index = self.layer_hierarchy.index(target_layer)

            # Can only import from same layer or inner layers (lower index)
            return target_index <= source_index
        except ValueError:
            # If layer not found in hierarchy, be permissive
            return True

    def extract_imports_from_file(self, file_path: Path) -> List[Tuple[int, str]]:
        """Extract all import statements from a Python file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append((node.lineno, alias.name))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append((node.lineno, node.module))

            return imports

        except (SyntaxError, UnicodeDecodeError, Exception) as e:
            print(f"Warning: Could not parse {file_path}: {e}")
            return []

    def get_module_layer_from_path(self, file_path: Path) -> ArchitecturalLayer:
        """Determine the architectural layer based on the file path"""
        relative_path = file_path.relative_to(self.project_root)
        parts = relative_path.parts

        if len(parts) == 0:
            return ArchitecturalLayer.EXTERNAL

        first_part = parts[0]

        if first_part == LAYER_ABSTRACTION:
            return ArchitecturalLayer.ABSTRACTION
        elif first_part == LAYER_DOMAIN:
            return ArchitecturalLayer.DOMAIN
        elif first_part == LAYER_APPLICATION:
            return ArchitecturalLayer.APPLICATION
        elif first_part.startswith(LAYER_ADAPTER_PREFIX):
            return ArchitecturalLayer.ADAPTER
        elif first_part.startswith(LAYER_PLUGIN_PREFIX):
            return ArchitecturalLayer.PLUGIN
        elif first_part == LAYER_HELPERS:
            return ArchitecturalLayer.HELPERS
        else:
            return ArchitecturalLayer.EXTERNAL

    def check_file(self, file_path: Path) -> None:
        """Check a single Python file for import violations"""
        if not file_path.suffix == ".py":
            return

        source_layer = self.get_module_layer_from_path(file_path)
        if source_layer == ArchitecturalLayer.EXTERNAL:
            return  # Skip files not in our architecture

        imports = self.extract_imports_from_file(file_path)

        for line_number, imported_module in imports:
            target_layer = self.categorize_module_layer(imported_module)

            if not self.is_import_allowed(source_layer, target_layer, imported_module):
                # Determine specific reason for violation
                if (
                    target_layer == ArchitecturalLayer.EXTERNAL
                    and self.is_external_library(imported_module)
                ):
                    reason = (
                        f"{source_layer.name} layer cannot import external library "
                        f"'{imported_module}'. External libraries are only allowed "
                        f"in PLUGIN layer"
                    )
                else:
                    reason = (
                        f"{source_layer.name} layer cannot import from "
                        f"{target_layer.name} layer"
                    )

                violation = ImportViolation(
                    file_path=str(file_path.absolute()),
                    line_number=line_number,
                    imported_module=imported_module,
                    violating_import=imported_module,
                    source_layer=source_layer,
                    target_layer=target_layer,
                    reason=reason,
                )
                self.violations.append(violation)

    def check_directory(self, directory: Path) -> None:
        """Recursively check all Python files in a directory"""
        for root, dirs, files in os.walk(directory):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != "__pycache__"]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    self.check_file(file_path)

    def run_check(self) -> None:
        """Run the complete clean architecture check"""
        if not self.project_root.exists():
            print(f"Error: Project root '{self.project_root}' does not exist")
            return

        print(f"Checking Clean Architecture compliance in {self.project_root}")
        print(
            "Architecture layers (innermost → outermost): "
            f"{' → '.join(layer.name for layer in self.layer_hierarchy)}"
        )
        print()

        self.check_directory(self.project_root)

    def print_results(self, verbose: bool = False) -> None:
        """Print the results of the architecture check"""
        if not self.violations:
            print("✅ No Clean Architecture violations found!")
            return

        print(f"❌ Found {len(self.violations)} Clean Architecture violations:")
        print()

        # Group violations by file
        violations_by_file: dict[str, List[ImportViolation]] = {}
        for violation in self.violations:
            if violation.file_path not in violations_by_file:
                violations_by_file[violation.file_path] = []
            violations_by_file[violation.file_path].append(violation)

        for file_path in sorted(violations_by_file.keys()):
            for violation in violations_by_file[file_path]:
                # PyCharm-compatible clickable link format
                print(f'  File "{violation.file_path}", line {violation.line_number}')
                print(f"    Import: {violation.imported_module}")
                print(f"    ❌ {violation.reason}")
                if verbose:
                    print(
                        f"    Source: {violation.source_layer.name}, "
                        f"Target: {violation.target_layer.name}"
                    )
                print()

    def get_summary(self) -> Dict[str, int]:
        """Get a summary of violations by layer"""
        summary: dict[str, int] = {}
        for violation in self.violations:
            key = f"{violation.source_layer.name} → {violation.target_layer.name}"
            summary[key] = summary.get(key, 0) + 1
        return summary


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Check Clean Architecture compliance for OTCloud"
    )
    parser.add_argument(
        "--path",
        default=PROJECT_NAME,
        help=f"Path to {PROJECT_NAME} project directory",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed violation information",
    )

    args = parser.parse_args()

    checker = CleanArchitectureChecker(args.path)
    checker.run_check()
    checker.print_results(verbose=args.verbose)

    if checker.violations:
        print("\n📊 Violation Summary:")
        summary = checker.get_summary()
        for violation_type, count in sorted(summary.items()):
            print(f"  {violation_type}: {count}")

        print(f"\nTotal violations: {len(checker.violations)}")
        sys.exit(1)
    else:
        print("🎉 All imports follow Clean Architecture principles!")
        sys.exit(0)


if __name__ == "__main__":
    main()
