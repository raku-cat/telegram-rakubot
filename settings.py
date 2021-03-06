import os
import asyncio
import aiofiles
import json
import sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DEFINITIONS_ROOT = os.path.join(PROJECT_ROOT, 'src', 'definitions')

def getKeys():
    with open(sys.path[0] + '/keys.json') as f:
        keys = json.loads(f.read())
    return keys
