#!/bin/bash

# Entity Tracker - Setup Script
# This script sets up the entity tracker environment

set -e  # Exit on error

echo "================================================"
echo "Entity Tracker - Setup Script"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Python $required_version or higher is required (found $python_version)"
    exit 1
else
    echo "✓ Python $python_version detected"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Set up environment file
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys before running the agent"
    echo "   Required: OPENAI_API_KEY"
    echo "   Optional: TAVILY_API_KEY"
else
    echo "✓ .env file already exists"
fi

# Run tests
echo ""
read -p "Run tests to verify installation? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running tests..."
    pytest
    echo "✓ Tests completed"
fi

# Print next steps
echo ""
echo "================================================"
echo "Setup Complete! 🎉"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your API keys"
echo "  2. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo "  3. Run an example:"
echo "     python examples/basic_tracking.py"
echo ""
echo "For more information, see:"
echo "  - QUICKSTART.md"
echo "  - README.md"
echo ""
echo "Happy tracking! 🎯"
echo ""

