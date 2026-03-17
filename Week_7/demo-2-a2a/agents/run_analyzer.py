#!/usr/bin/env python3
"""Start the Analyzer A2A agent server."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import uvicorn
from agents.analyzer import AnalyzerAgent
from config import ANALYZER_PORT

agent = AnalyzerAgent()

if __name__ == "__main__":
    uvicorn.run(agent.app, host="0.0.0.0", port=ANALYZER_PORT, log_level="info")
