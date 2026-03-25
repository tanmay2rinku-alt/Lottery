#!/usr/bin/env python3
"""
Simple health check server for Railway deployment
"""

from flask import Flask
import os

app = Flask(__name__)

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'lottery-scraper'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)