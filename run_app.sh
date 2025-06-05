#!/bin/bash

# Find the process using port 5000 and kill it
PID=$(lsof -ti tcp:5000)
if [ -n "$PID" ]; then
  echo "Killing process on port 5000: $PID"
  kill -9 $PID
else
  echo "No process found on port 5000"
fi

# Run the Flask app on port 5000
/home/gravitywaves/GravityWaves/.venv/bin/python /home/gravitywaves/GravityWaves/app.py --port 5000
