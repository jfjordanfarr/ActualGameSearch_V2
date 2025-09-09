#!/usr/bin/env python3
"""
Simple local API server for testing the search functionality
Uses our fixed SQLite database directly - no Cloudflare dependencies
"""

import sqlite3
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.parse

class SearchAPIHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.db_path = Path("pipeline/data/phase2_hybrid_search.db")
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # CORS headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if path == '/search':
                response = self.handle_search(query_params)
            elif path == '/apps':
                response = self.handle_apps(query_params)
            elif path == '/health':
                response = {"status": "ok", "database": "connected"}
            else:
                response = {"error": "Not found", "available_endpoints": ["/search", "/apps", "/health"]}
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())
    
    def handle_search(self, params):
        """Handle search requests"""
        query = params.get('q', [''])[0]
        limit = int(params.get('limit', ['10'])[0])
        
        if not query:
            return {"error": "Query parameter 'q' is required"}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # FTS5 search
        cursor.execute('''
            SELECT r.id, r.review, a.name, a.appid, a.tags
            FROM reviews_fts fts
            JOIN reviews r ON r.id = fts.rowid  
            JOIN apps a ON r.appid = a.appid
            WHERE reviews_fts MATCH ?
            LIMIT ?
        ''', (query, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "review_id": row[0],
                "review_text": row[1][:200] + "..." if len(row[1]) > 200 else row[1],
                "app_name": row[2],
                "app_id": row[3],
                "tags": row[4]
            })
        
        conn.close()
        
        return {
            "query": query,
            "results_count": len(results),
            "results": results
        }
    
    def handle_apps(self, params):
        """Handle apps listing"""
        limit = int(params.get('limit', ['10'])[0])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT appid, name, short_description, tags, price_final, is_free
            FROM apps 
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "app_id": row[0],
                "name": row[1],
                "description": row[2],
                "tags": row[3],
                "price": row[4],
                "is_free": bool(row[5])
            })
        
        conn.close()
        
        return {
            "apps_count": len(results),
            "apps": results
        }

def run_server(port=8787):
    """Run the local API server"""
    server = HTTPServer(('localhost', port), SearchAPIHandler)
    print(f"🚀 ActualGameSearch Local API Server")
    print(f"📍 Running on http://localhost:{port}")
    print(f"🔍 Try: http://localhost:{port}/search?q=fun")
    print(f"📱 Try: http://localhost:{port}/apps?limit=5")
    print(f"❤️  Try: http://localhost:{port}/health")
    print(f"\n🛑 Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n👋 Server stopped")
        server.shutdown()

if __name__ == "__main__":
    run_server()
