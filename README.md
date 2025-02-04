# Tides Pipeline

The Tides Pipeline is a modular data processing pipeline designed to handle the ingestion, classification, and database updating of astronomical spectra. The pipeline is highly configurable and can be run for a specific night or a list of objects.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Modules](#modules)
  - [Data Ingestion](#data-ingestion)
  - [Classification](#classification)
  - [Database Update](#database-update)
- [Logging](#logging)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/wisemanp/tides_pipeline.git
    cd tides_pipeline
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration

The pipeline is configured using a YAML file. The default configuration file is located at config/config.yml. You can specify a different configuration file using the `--config` argument when running the pipeline.

Example configuration:
```yaml
base_dir: "/path/to/base"
deliveries_dir: "/path/to/base/deliveries"
spectra_dir: "/path/to/base/spectra"
archive_dir: "/path/to/base/archive"
log_dir: "/path/to/base/logs"
modules:
  - data_ingestion
  - classification
  - db_update
classification:
  codes:
    - code: "snid"
      config_file: "/path/to/snid/config.yml"
    - code: "ngsf"
      config_file: "/path/to/ngsf/config.yml"
    - code: "siren"
      config_file: "/path/to/siren/config.yml"