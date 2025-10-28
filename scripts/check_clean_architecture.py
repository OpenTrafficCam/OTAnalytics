#!/usr/bin/env python3
"""
Clean Architecture Import Checker for OTAnalytics

This script validates that the OTAnalytics project follows Clean Architecture import
rules. The architecture has 4 layers:
1. domain (innermost layer)
2. application
3. adapter_*
4. plugin_* (outermost layer)

Import Rules:
- Modules can only import from the same layer or inner (more central) layers
- Domain can only import from domain and standard libraries
- Application can import from domain, application, and standard libraries
- Adapter can import from domain, application, adapter, and standard libraries
- Plugin can import from all layers and standard libraries
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


class ArchitecturalLayer(Enum):
    """Defines the architectural layers in order from innermost to outermost"""

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
    def __init__(self, project_root: str = "OTAnalytics"):
        self.project_root = Path(project_root)
        self.violations: List[ImportViolation] = []

        # Define layer hierarchy (inner to outer)
        self.layer_hierarchy = [
            ArchitecturalLayer.DOMAIN,
            ArchitecturalLayer.APPLICATION,
            ArchitecturalLayer.ADAPTER,
            ArchitecturalLayer.PLUGIN,
            ArchitecturalLayer.HELPERS,
        ]

    def categorize_module_layer(self, module_name: str) -> ArchitecturalLayer:
        """Determine which architectural layer a module belongs to"""
        if not module_name.startswith("OTAnalytics"):
            return ArchitecturalLayer.EXTERNAL

        parts = module_name.split(".")
        if len(parts) < 2:
            return ArchitecturalLayer.EXTERNAL

        layer_part = parts[1]  # OTAnalytics.<layer_part>

        if layer_part == "domain":
            return ArchitecturalLayer.DOMAIN
        elif layer_part == "application":
            return ArchitecturalLayer.APPLICATION
        elif layer_part.startswith("adapter_"):
            return ArchitecturalLayer.ADAPTER
        elif layer_part.startswith("plugin_"):
            return ArchitecturalLayer.PLUGIN
        elif layer_part == "helpers":
            return ArchitecturalLayer.HELPERS
        else:
            # Unknown OTAnalytics module, treat as external
            return ArchitecturalLayer.EXTERNAL

    def is_import_allowed(
        self, source_layer: ArchitecturalLayer, target_layer: ArchitecturalLayer
    ) -> bool:
        """Check if importing from target_layer to source_layer is allowed"""
        if target_layer == ArchitecturalLayer.EXTERNAL:
            return True  # All layers can import external modules

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

        if first_part == "domain":
            return ArchitecturalLayer.DOMAIN
        elif first_part == "application":
            return ArchitecturalLayer.APPLICATION
        elif first_part.startswith("adapter_"):
            return ArchitecturalLayer.ADAPTER
        elif first_part.startswith("plugin_"):
            return ArchitecturalLayer.PLUGIN
        elif first_part == "helpers":
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

            if not self.is_import_allowed(source_layer, target_layer):
                violation = ImportViolation(
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=line_number,
                    imported_module=imported_module,
                    violating_import=imported_module,
                    source_layer=source_layer,
                    target_layer=target_layer,
                    reason=f"{source_layer.name} layer cannot import from "
                    f"{target_layer.name} layer",
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
            print(f"📄 {file_path}:")
            for violation in violations_by_file[file_path]:
                print(f"  Line {violation.line_number}: {violation.imported_module}")
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
        description="Check Clean Architecture compliance for OTAnalytics"
    )
    parser.add_argument(
        "--path",
        default="OTAnalytics",
        help="Path to OTAnalytics project directory",
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
