#!/usr/bin/env python
"""AI Travel Platform — Start Backend Server"""
import subprocess, sys, os

os.chdir(os.path.join(os.path.dirname(__file__), "services", "planner-api"))
subprocess.run([
    sys.executable, "-m", "uvicorn", "app.main:app",
    "--host", "0.0.0.0", "--port", "8001", "--reload"
])
