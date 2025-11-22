#!/bin/bash
# Quick Start Script for AI Code Remediation Microservice (Linux/Mac)

echo "==========================================================================="
echo "AI CODE REMEDIATION MICROSERVICE - QUICK START"
echo "==========================================================================="
echo ""

# Check Python version
echo "[1/6] Checking Python version..."
python_version=$(python3 --version 2>&1)
if [[ $python_version =~ Python\ 3\.([0-9]+) ]]; then
    minor_version=${BASH_REMATCH[1]}
    if [ $minor_version -ge 10 ]; then
        echo "✓ Python version OK: $python_version"
    else
        echo "✗ Python 3.10+ required. Found: $python_version"
        exit 1
    fi
else
    echo "✗ Python not found or version check failed"
    exit 1
fi

# Create virtual environment
echo ""
echo "[2/6] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "✓ Virtual environment already exists"
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "[3/6] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "[4/6] Installing dependencies (this may take 5-10 minutes)..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create necessary directories
echo ""
echo "[5/6] Verifying project structure..."
mkdir -p app/rag/recipes app/utils
echo "✓ Project structure verified"

# Display next steps
echo ""
echo "[6/6] Setup complete!"
echo ""
echo "==========================================================================="
echo "NEXT STEPS:"
echo "==========================================================================="
echo ""
echo "1. Start the service:"
echo "   uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "2. In a new terminal, run tests:"
echo "   python test_local.py"
echo ""
echo "3. Access API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "==========================================================================="
echo ""
echo "Starting AI Code Remediation Microservice..."
echo ""
uvicorn app.main:app --host 0.0.0.0 --port 8000
