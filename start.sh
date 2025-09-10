#!/bin/bash

# Dosya yapısını kontrol et
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

# app.py dosyasını bul
echo "Looking for app.py:"
find . -name "app.py" -type f

# Python path'ini kontrol et
echo "Python version:"
python --version

# app.py'yi çalıştırmaya çalış
if [ -f "app.py" ]; then
    echo "Found app.py in current directory, running it..."
    python app.py
elif [ -f "./app.py" ]; then
    echo "Found app.py with relative path, running it..."
    python ./app.py
else
    echo "app.py not found, searching in subdirectories..."
    APP_PATH=$(find . -name "app.py" -type f | head -1)
    if [ -n "$APP_PATH" ]; then
        echo "Found app.py at: $APP_PATH"
        python "$APP_PATH"
    else
        echo "app.py not found anywhere!"
        exit 1
    fi
fi
