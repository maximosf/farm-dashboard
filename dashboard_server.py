"""
Dashboard Server for Railway/Render deployment
"""
import json, os, glob
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

STATUS_DIR = os.environ.get('STATUS_DIR', '/tmp/dashboard')

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path

        if path == '/' or path == '/dashboard':
            try:
                with open('dashboard.html', 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.end_headers()
                self.wfile.write(content)
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
                return

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if path.startswith('/status/'):
            phone = path.split('/')[-1]
            fpath = os.path.join(STATUS_DIR, f'phone_{phone}_status.json')
            if os.path.exists(fpath):
                with open(fpath) as f:
                    self.wfile.write(f.read().encode())
            else:
                self.wfile.write(b'null')

        elif path.startswith('/update/'):
            # POST-like via GET for simplicity - data in query string
            self.wfile.write(b'{}')

        elif path == '/all':
            result = {}
            os.makedirs(STATUS_DIR, exist_ok=True)
            for fpath in glob.glob(os.path.join(STATUS_DIR, 'phone_*_status.json')):
                num = os.path.basename(fpath).split('_')[1]
                try:
                    with open(fpath) as f:
                        result[num] = json.load(f)
                except: pass
            self.wfile.write(json.dumps(result).encode())
        else:
            self.wfile.write(b'{}')

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if path.startswith('/update/'):
            phone = path.split('/')[-1]
            os.makedirs(STATUS_DIR, exist_ok=True)
            fpath = os.path.join(STATUS_DIR, f'phone_{phone}_status.json')
            with open(fpath, 'wb') as f:
                f.write(body)
            self.wfile.write(b'{"ok":true}')
        else:
            self.wfile.write(b'{}')

if __name__ == '__main__':
    os.makedirs(STATUS_DIR, exist_ok=True)
    port = int(os.environ.get('PORT', 5050))
    print(f'Dashboard running on port {port}')
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()
