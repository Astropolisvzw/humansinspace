import socket
import ujson
import utime
import config

class SimpleWebServer:
    def __init__(self, port=80):
        self.port = port
        self.latest_data = None
        self.last_updated = None
        self.config = config.load_config()

    def set_data(self, data, timestamp):
        """Store the latest API data and timestamp"""
        self.latest_data = data
        self.last_updated = timestamp

    def start(self):
        """Start the web server in non-blocking mode"""
        addr = socket.getaddrinfo('0.0.0.0', self.port)[0][-1]
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(addr)
        self.sock.listen(1)
        self.sock.setblocking(False)
        print(f'Web server listening on port {self.port}')

    def handle_request(self):
        """Handle incoming HTTP requests (non-blocking)"""
        try:
            cl, addr = self.sock.accept()
            print('Client connected from', addr)

            cl.settimeout(1.0)
            request = cl.recv(1024).decode('utf-8')

            # Parse request method and path
            request_line = request.split('\r\n')[0]
            method = request_line.split()[0] if request_line else 'GET'
            path = request_line.split()[1] if len(request_line.split()) > 1 else '/'

            if method == 'POST' and '/api/config/wifi' in path:
                # Handle WiFi configuration
                try:
                    # Extract POST data
                    body_start = request.find('\r\n\r\n') + 4
                    body = request[body_start:]
                    # Parse form data
                    params = {}
                    for param in body.split('&'):
                        if '=' in param:
                            key, value = param.split('=', 1)
                            # URL decode
                            value = value.replace('+', ' ')
                            params[key] = value

                    if 'ssid' in params and 'password' in params:
                        config.add_wifi_network(params['ssid'], params['password'])
                        response = """HTTP/1.1 303 See Other
Location: /
Content-Type: text/plain

WiFi network added"""
                    else:
                        response = """HTTP/1.1 400 Bad Request
Content-Type: text/plain

Missing ssid or password"""
                except Exception as e:
                    response = f"""HTTP/1.1 500 Internal Server Error
Content-Type: text/plain

Error: {e}"""

            elif method == 'POST' and '/api/config/wifi/delete' in path:
                # Handle WiFi network deletion
                try:
                    body_start = request.find('\r\n\r\n') + 4
                    body = request[body_start:]
                    params = {}
                    for param in body.split('&'):
                        if '=' in param:
                            key, value = param.split('=', 1)
                            value = value.replace('+', ' ')
                            params[key] = value

                    if 'ssid' in params:
                        config.remove_wifi_network(params['ssid'])
                        self.config = config.load_config()
                        response = """HTTP/1.1 303 See Other
Location: /
Content-Type: text/plain

WiFi network removed"""
                    else:
                        response = """HTTP/1.1 400 Bad Request
Content-Type: text/plain

Missing ssid parameter"""
                except Exception as e:
                    response = f"""HTTP/1.1 500 Internal Server Error
Content-Type: text/plain

Error: {e}"""

            elif method == 'POST' and '/api/config/interval' in path:
                # Handle update interval configuration
                try:
                    body_start = request.find('\r\n\r\n') + 4
                    body = request[body_start:]
                    params = {}
                    for param in body.split('&'):
                        if '=' in param:
                            key, value = param.split('=', 1)
                            params[key] = value

                    if 'hours' in params:
                        hours = int(params['hours'])
                        config.set_update_interval(hours)
                        self.config = config.load_config()
                        response = """HTTP/1.1 303 See Other
Location: /
Content-Type: text/plain

Update interval changed"""
                    else:
                        response = """HTTP/1.1 400 Bad Request
Content-Type: text/plain

Missing hours parameter"""
                except Exception as e:
                    response = f"""HTTP/1.1 500 Internal Server Error
Content-Type: text/plain

Error: {e}"""

            elif 'GET /api/latest' in request:
                # Return JSON data
                if self.latest_data:
                    response_data = {
                        'data': self.latest_data,
                        'last_updated': self.last_updated,
                        'timestamp': utime.time()
                    }
                    response_json = ujson.dumps(response_data)
                    response = f"""HTTP/1.1 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: *

{response_json}
"""
                else:
                    response = """HTTP/1.1 503 Service Unavailable
Content-Type: application/json

{"error": "No data available yet"}
"""
            elif 'GET /' in request:
                # Return HTML page with API documentation
                html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Humans in Space - API</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            line-height: 1.6;
        }}
        h1 {{ color: #333; margin-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; border-bottom: 2px solid #e74c3c; padding-bottom: 5px; }}
        .subtitle {{ color: #666; font-size: 14px; margin-bottom: 30px; }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .number {{
            font-size: 72px;
            color: #e74c3c;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }}
        .updated {{
            color: #666;
            font-size: 14px;
            text-align: center;
            margin-bottom: 20px;
        }}
        .person {{
            padding: 8px;
            border-bottom: 1px solid #eee;
        }}
        .craft {{
            color: #3498db;
            font-weight: bold;
        }}
        .endpoint {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 12px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            margin: 10px 0;
        }}
        .method {{
            background: #27ae60;
            color: white;
            padding: 4px 8px;
            border-radius: 3px;
            font-weight: bold;
            font-size: 12px;
            margin-right: 8px;
        }}
        code {{
            background: #ecf0f1;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 13px;
        }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .example {{ margin: 15px 0; }}
    </style>
</head>
<body>
    <h1>Humans in Space</h1>
    <div class="subtitle">Real-time astronaut data from the International Space Station and other spacecraft</div>

    <div class="card">
"""
                if self.latest_data:
                    num = self.latest_data.get('number', 0)
                    html += f'<div class="number">{num}</div>'
                    html += f'<div class="updated">Last updated: {self.last_updated}</div>'
                    html += '<h3>Currently in space:</h3>'

                    for person in self.latest_data.get('people', []):
                        name = person.get('name', 'Unknown')
                        craft = person.get('craft', 'Unknown')
                        html += f'<div class="person"><span class="craft">{craft}</span> - {name}</div>'
                else:
                    html += '<p>No data available yet</p>'

                html += """
    </div>

    <div class="card">
        <h2>WiFi Configuration</h2>
        <p>Configured WiFi networks (tried in order):</p>

        <div style="margin: 20px 0;">
"""
                # List configured WiFi networks
                wifi_networks = config.get_wifi_networks()
                if wifi_networks:
                    for network in wifi_networks:
                        ssid = network.get('ssid', 'Unknown')
                        # Check if it's from config.json (can be deleted) or secrets.py (read-only)
                        config_networks = self.config.get('wifi_networks', [])
                        can_delete = any(n['ssid'] == ssid for n in config_networks)

                        html += f"""
            <div style="padding: 10px; border: 1px solid #eee; border-radius: 4px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: bold;">{ssid}</span>
"""
                        if can_delete:
                            html += f"""
                <form method="POST" action="/api/config/wifi/delete" style="margin: 0;">
                    <input type="hidden" name="ssid" value="{ssid}">
                    <button type="submit" style="background: #e74c3c; color: white; padding: 5px 10px; border: none; border-radius: 3px; cursor: pointer; font-size: 12px;">
                        Delete
                    </button>
                </form>
"""
                        else:
                            html += """
                <span style="font-size: 12px; color: #666;">(from secrets.py)</span>
"""
                        html += """
            </div>
"""
                else:
                    html += """
            <p style="color: #666;">No networks configured yet.</p>
"""

                html += """
        </div>

        <h3 style="margin-top: 30px;">Add New Network</h3>
        <form method="POST" action="/api/config/wifi" style="margin-top: 20px;">
            <div style="margin-bottom: 15px;">
                <label for="ssid" style="display: block; margin-bottom: 5px; font-weight: bold;">Network Name (SSID):</label>
                <input type="text" id="ssid" name="ssid" required
                       style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box;">
            </div>
            <div style="margin-bottom: 15px;">
                <label for="password" style="display: block; margin-bottom: 5px; font-weight: bold;">Password:</label>
                <input type="password" id="password" name="password" required
                       style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box;">
            </div>
            <button type="submit"
                    style="background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px;">
                Add Network
            </button>
        </form>

        <p style="margin-top: 20px; font-size: 13px; color: #666;">
            Note: Device will restart to apply changes.
        </p>
    </div>"""


                html += f"""
    <div class="card">
        <h2>Update Interval</h2>
        <p>Configure how often the device fetches new astronaut data.</p>
        <p style="font-weight: bold; color: #27ae60;">Current interval: {self.config.get('update_interval_hours', 6)} hours</p>

        <form method="POST" action="/api/config/interval" style="margin-top: 20px;">
            <div style="margin-bottom: 15px;">
                <label for="hours" style="display: block; margin-bottom: 5px; font-weight: bold;">New Interval (hours):</label>
                <input type="number" id="hours" name="hours" min="1" max="24" value="{self.config.get('update_interval_hours', 6)}" required
                       style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box;">
            </div>
            <button type="submit"
                    style="background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px;">
                Update Interval
            </button>
        </form>

        <p style="margin-top: 20px; font-size: 13px; color: #666;">
            Note: Changes take effect after the next update cycle.
        </p>
    </div>

"""
                html += """
    <div class="card">
        <h2>API Documentation</h2>

        <h3>Get Latest Astronaut Data</h3>
        <div class="endpoint">
            <span class="method">GET</span>
            <span>/api/latest</span>
        </div>
        <p>Returns the latest astronaut data including all people currently in space, the total count, and when the data was last updated.</p>

        <div class="example">
            <strong>Response Format:</strong>
            <pre>{
  "data": {
    "number": 12,
    "message": "success",
    "people": [
      {
        "name": "Oleg Kononenko",
        "craft": "ISS"
      },
      ...
    ]
  },
  "last_updated": "14:30",
  "timestamp": 1733408444
}</pre>
        </div>

        <div class="example">
            <strong>Example Usage:</strong>
            <pre>curl http://192.168.5.216/api/latest</pre>
        </div>

        <div class="example">
            <strong>JavaScript Example:</strong>
            <pre>fetch('http://192.168.5.216/api/latest')
  .then(response => response.json())
  .then(data => {
    console.log(`${data.data.number} humans in space`);
    console.log(`Last updated: ${data.last_updated}`);
  });</pre>
        </div>

        <h3>Response Fields</h3>
        <ul>
            <li><code>data</code> - The astronaut data from the Open Notify API</li>
            <li><code>data.number</code> - Total number of humans currently in space</li>
            <li><code>data.people</code> - Array of people with <code>name</code> and <code>craft</code> fields</li>
            <li><code>last_updated</code> - Time when data was last fetched (HH:MM format, CET timezone)</li>
            <li><code>timestamp</code> - Unix timestamp of when this response was generated</li>
        </ul>
    </div>

    <div class="card">
        <h2>About</h2>
        <p>This data is provided by the <a href="http://api.open-notify.org/" target="_blank">Open Notify API</a> and displayed on a Raspberry Pi Pico W with a Waveshare 2.9" e-Paper display.</p>
        <p>The display shows the data in landscape mode with a prominent red number and spacecraft information.</p>
    </div>
</body>
</html>
"""
                response = f"""HTTP/1.1 200 OK
Content-Type: text/html

{html}
"""
            else:
                response = """HTTP/1.1 404 Not Found
Content-Type: text/plain

Not Found
"""

            cl.send(response.encode('utf-8'))
            cl.close()

        except OSError:
            # No connection available (non-blocking)
            pass
        except Exception as e:
            print('Error handling request:', e)
