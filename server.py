import shutil
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

class LogHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)

        # only supoprt the /tail endpoint
        if url.path != "/tail":
            self.respond(404, b"404 Not Found")
            return

        # extract params and escape single-quotes for use in $'' ANSI-C Quoting to prevent
        # command injection security issues
        query_params = parse_qs(url.query)
        file = (query_params.get("file", [""])[0]).replace("'", "\\'")
        limit = (query_params.get("limit", [""])[0]).replace("'", "\\'")
        grep = (query_params.get("keyword", [""])[0]).replace("'", "\\'")
        tail_cmd = "tac" if shutil.which("tac") is not None else "tail -r"
        grep_filter = "" if grep == "" else f"| (grep -a $'{grep}' || true)"
        limit_filter = "" if limit == "" else f"| head -n $'{limit}'"
        command = f"set -o pipefail; {tail_cmd} $'/var/log/{file}' {grep_filter} {limit_filter}"

        # require file query param
        if file == "":
            self.respond(500, b"`file` parameter missing")
            return

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, executable="/bin/bash")

            # exit code 141 is treated as success. it indicates termination by SIGPIPE, which occurs when output
            # is truncated by head(1)
            if result.returncode in (0, 141):
                self.respond(200, result.stdout.encode("utf-8"))
            else:
                raise subprocess.CalledProcessError(result.returncode, command, stderr=result.stderr)

        except Exception as e:
            messages = [str(e).encode("utf-8"), b"\n"]

            match e:
                # if the error is from the command, emit the programs stderr
                case subprocess.CalledProcessError(stderr=stderr):
                    messages.append(e.stderr.encode("utf-8"))
                    messages.append(b"\n")

            self.respond(500, *messages)

    def respond(self, response_code, *messages):
        self.send_response(response_code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        for message in messages:
            self.wfile.write(message)

def run(server_class=HTTPServer, handler_class=LogHandler, port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
