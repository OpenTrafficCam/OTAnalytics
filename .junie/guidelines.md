# OTAnalytics Developer Guidelines

## Project Overview

OTAnalytics is a core module of the OpenTrafficCam framework designed to perform traffic analysis on trajectories of
road users. It processes trajectory data, defines traffic flows, counts vehicles, and generates statistics.

## Project Structure

The project follows a clean architecture approach with clear separation of concerns:

```structure
OTAnalytics/
├── OTAnalytics/              # Main package
│   ├── domain/               # Domain models and business logic
│   ├── application/          # Use cases and application services
│   ├── adapter_*/            # Adapters for external interfaces
│   ├── plugin_*/             # Plugins for various functionalities
│   └── helpers/              # Utility functions
├── tests/                    # Test suite
│   ├── OTAnalytics/          # Unit tests mirroring package structure
│   ├── utils/                # Test utilities and builders
│   ├── data/                 # Test data
│   ├── conftest.py           # Test fixtures
│   ├── benchmark_*.py        # Benchmark tests
│   └── regression_*.py       # Regression tests
├── .run/                     # Run configurations
├── scripts/                  # Utility scripts
└── examples/                 # Example files
```

## Tech Stack

- **Language**: Python 3.12+
- **GUI Frameworks**: CustomTkinter, NiceGUI
- **Web Frameworks**: FastAPI, Uvicorn
- **Data Processing**: Pandas, NumPy, Shapely
- **Visualization**: Matplotlib, Seaborn
- **Testing**: pytest, pytest-cov, pytest-benchmark
- **Code Quality**: Black, Flake8, isort, mypy, pre-commit
- **Build Tool**: Hatch

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/OpenTrafficCam/OTAnalytics.git
   cd OTAnalytics
   ```

2. **Install development dependencies**:

- Linux/macOS: `./install_dev.sh`
- Windows: `install_dev.cmd`


3. **Activate the virtual environment**:

- `source venv/bin/activate`

## Running the Application

- **GUI Mode**:
  - Linux/macOS: `./start_gui.sh`
  - Windows: `start_gui.cmd`

- **CLI Mode**:
  - Linux/macOS: `./start_gui.sh --cli`
  - Windows: `start_gui.cmd --cli`

## Testing

- **Run all tests**:
  ```bash
  python -m pytest
  ```

- **Run tests with coverage**:
  ```bash
  python -m pytest --cov=OTAnalytics
  ```

- **Run benchmark tests**:
  ```bash
  python -m pytest tests/benchmark_otanalytics.py
  ```

## Best Practices

1. **Code Style**:

- Follow PEP 8 guidelines
- Use Black for code formatting (line length 88)
- Sort imports with isort
- Use mypy for static type checking
- Add type hints to all functions and methods

2. **Testing**:

- Write tests for all new functionality
- Use fixtures from conftest.py when possible
- Use builders in tests/utils for test data creation
- Use pytest as the main testing framework
- Use unittest.mock as the mock object library
- Tests are organized to mirror the application structure

3. **Git Workflow**:

- Create feature branches from main
- Run pre-commit hooks before committing
- Write descriptive commit messages
- Create pull requests for code review

4. **Documentation**:

- Add docstrings to all public classes and methods
- Keep the README.md updated with new features
- Document complex algorithms and design decisions
- Adhere to Google Style Python Docstrings

5. **Architecture**:

- Maintain separation between domain, application, and infrastructure
- Use dependency injection for better testability
- Follow the plugin pattern for extensions
- Maintain separation of concerns between layers

## Common Tasks

- Adding a new plugin: Create a new directory in `OTAnalytics/plugin_*`
- Adding tests: Mirror the application structure in the `tests` directory
