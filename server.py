import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

class LogHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        query_params = parse_qs(url.query)

        file = query_params.get("file", [""])[0]
        limit = query_params.get("limit", [""])[0]
        grep = query_params.get("keyword", [""])[0]
        grep_filter = "" if grep == "" else f"| grep {grep}"
        limit_filter = "" if limit == "" else f"| head -n {limit}"
        command = f"set -o pipefail; tail -r /var/log/{file} {grep_filter} {limit_filter}"

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)

            exit_code = result.returncode
            
            if exit_code == 0 or exit_code == 141:
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(result.stdout.encode("utf-8"))
            else:
                print("stdout: "+ result.stdout)
                print("stderr: "+result.stderr)
                raise subprocess.CalledProcessError(result.returncode, command, stderr=result.stderr)

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(str(e).encode("utf-8"))
            self.wfile.write("\n".encode("utf-8"))

            match e:
                case subprocess.CalledProcessError(stderr=stderr):
                    self.wfile.write(e.stderr.encode("utf-8"))
                    self.wfile.write("\n".encode("utf-8"))


def run(server_class=HTTPServer, handler_class=LogHandler, port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
