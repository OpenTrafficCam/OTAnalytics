# OTAnalytics

[![PyPI version](https://img.shields.io/pypi/v/OTAnalytics.svg)](https://pypi.org/p/OTAnalytics/)
[![Tests](https://github.com/OpenTrafficCam/OTAnalytics/actions/workflows/test.yml/badge.svg?tag=latest)](https://github.com/OpenTrafficCam/OTAnalytics/actions/workflows/test.yml?query=tag%3Alatest)
[![Tests](https://github.com/OpenTrafficCam/OTAnalytics/actions/workflows/build-release.yml/badge.svg)](https://github.com/OpenTrafficCam/OTAnalytics/actions/workflows/build-release.yml)

OTAnalytics is a core module of the [OpenTrafficCam framework](https://github.com/OpenTrafficCam) designed to perform
traffic analysis on trajectories of road users tracked by [OTVision](https://github.com/OpenTrafficCam/OTVision) or
other tools in videos recorded by [OTCamera](https://github.com/OpenTrafficCam/OTCamera) or other camera systems.

## Overview

OTAnalytics provides tools for analyzing traffic data, including:

- Processing trajectory data of road users
- Defining and analyzing traffic flows
- Counting vehicles/road users assigned to flows
- Generating event lists and statistics
- Visualizing traffic data

The application offers multiple user interfaces:

- A graphical desktop interface (using CustomTkinter)
- A command-line interface for automation and batch processing

## Installation

### Requirements

- Python 3.12 or higher
- Dependencies listed in [requirements.txt](requirements.txt)

### Installation from GitHub Releases (Recommended)

The easiest way to install OTAnalytics is to download the latest release from
the [GitHub Releases page](https://github.com/OpenTrafficCam/OTAnalytics/releases).

1. Go to the [OTAnalytics Releases page](https://github.com/OpenTrafficCam/OTAnalytics/releases)
2. Download the latest release for your operating system
3. Extract the downloaded archive
4. Run the application using the instructions in the [Usage](#usage) section

### Installation from Source (Linux/macOS)

If you prefer to install from source:

1. Clone the repository:

   ```bash
   git clone https://github.com/OpenTrafficCam/OTAnalytics.git
   cd OTAnalytics
   ```

2. Run the installation script:
   ```bash
   ./install.sh
   ```

### Installation from Source (Windows)

If you prefer to install from source:

1. Clone the repository:

   ```cmd
   git clone https://github.com/OpenTrafficCam/OTAnalytics.git
   cd OTAnalytics
   ```

2. Run the installation script:
   ```cmd
   install.cmd
   ```

## Usage

### Starting the Application

#### Desktop GUI (Default)

On Linux/macOS:

```bash
./start_gui.sh
```

On Windows:

```cmd
start_gui.cmd
```

#### Command Line Interface

On Linux/macOS:

```bash
./start_gui.sh --cli
```

On Windows:

```cmd
start_gui.cmd --cli
```

### Configuration

OTAnalytics can be configured using:

1. Command-line arguments
2. Configuration files (YAML format)

Example configuration options:

- Specify track files for analysis
- Define flow and section configurations using otflow files
- Configure export formats and counting intervals
- Control parallelization with multiple processes
- Include or exclude specific road user classes

## Features

- **Track Analysis**: Process and analyze trajectory data from various sources
- **Flow Definition**: Define and analyze traffic flows between sections
- **Counting**: Count road users assgined to flows with configurable time intervals
- **Event Detection**: Generate event lists when road users cross defined sections
- **Visualization**: Visualize tracks, flows, and sections
- **Export**: Export analysis results in various formats
- **Filtering**: Filter tracks by road user class and time
- **Parallelization**: Process data using multiple CPU cores

## Documentation

For detailed instructions on how to install and use OTAnalytics, please refer to
the [official documentation](https://opentrafficcam.org/OTAnalytics).

- [Installation Guide](https://opentrafficcam.org/OTAnalytics/installation/)
- [User Interface Guide](https://opentrafficcam.org/OTAnalytics/usage-ui/)

## Contributing

We appreciate your support in the form of both code and comments. Please have a look at
the [contribute](https://opentrafficcam.org/contribute) section of the OpenTrafficCam documentation for guidelines on
how to contribute to this project.

## License

This software is licensed under the [GPL-3.0 License](LICENSE)

## Contact

- GitHub: [https://github.com/OpenTrafficCam](https://github.com/OpenTrafficCam)
- Email: [team@opentrafficcam.org](mailto:team@opentrafficcam.org)
