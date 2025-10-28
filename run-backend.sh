#!/bin/bash

echo "🚀 Starting Backend Server..."
cd /workspaces/docker-in-docker-2/backend
source venv/bin/activate
python main.py
