# Synthetic Population Generator 2.0

## Features

For PopGen 2.1
* Automatic data validator
* Census data importer

For PopGen 2.2
* Output Data Analyzer with charting and table generation capabilities

## Installation

`pip install popgen`

## Setup

```python
from popgen import Project

project = Project('path/to/config/file')
project.load_project()
project.run_scenarios()
```