# RAYA Water Module

## Overview

The RAYA Water Module provides water-resource analysis,
forecasting and rainfall validation functionality.

## Project Structure

Raya_Water/
│
├── raya.c
├── README.md
├── build.bat
├── run.bat
├── run_validation.bat
├── test_resource_module.ps1
├── data/
└── assets/

## Requirements

- Windows
- GCC compiler
- PowerShell

## Build

Open a terminal inside the Raya_Water folder:

gcc raya.c -o raya.exe -lm

Or run:

build.bat

## Run

run.bat

## Validation

run_validation.bat

or:

raya.exe --validation

## Data

All required CSV files are included inside:

data/

## Portability

The project does not require absolute paths to files
outside this directory.

The entire Raya_Water directory can be copied to another
computer and built/run from its new location.

## Testing

Run:

powershell -ExecutionPolicy Bypass -File test_resource_module.ps1