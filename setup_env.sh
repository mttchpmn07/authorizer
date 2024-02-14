#!/bin/bash

# Check if the virtual environment folder exists
if [ ! -d "venv" ]; then
    # Setup the virtual environment
    python -m venv venv
    echo "Virtual environment created."
fi

# Activate the virtual environment
source venv/Scripts/activate

# Check if pip is up to date
python -m pip install --upgrade pip

# Install required packages
python -m pip install fastapi pydantic_settings uvicorn sqlalchemy python-dotenv validators

echo "Setup completed."