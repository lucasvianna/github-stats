# GitHub Stats

## Overview

The GitHub Stats is a Python script that gathers and analyzes metrics from GitHub repositories, providing insights into pull requests, coding times, and other key statistics.

## Features

- Fetches information about open and closed pull requests from a GitHub repository.
- Calculates coding time, pickup time, and pull request size.
- Categorizes pull requests based on coding time.
- Supports command-line options for customization.

## Getting Started

### Prerequisites

- Python 3.x
- Required Python packages: `requests`

Install the required packages using:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py repo_owner repo_name --summary-only
```

### Command-Line Options

- repo_owner: GitHub repository owner.
- repo_name: GitHub repository name.
- --summary-only: Print a summary of metrics without detailed information.
