from http.server import BaseHTTPRequestHandler, HTTPServer
import json

hostName = "localhost"
serverPort = 8080

def read_file(filename):
	f = open(filename, "r")
	t = f.read()
	f.close()
	return t

def write_file(filename, content):
	f = open(filename, "w")
	f.write(content)
	f.close()

def get(path):
	if path == "/":
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": read_file("index.html")
		}
	elif path == "/tasks.json":
		return {
			"status": 200,
			"headers": {
				"Content-Type": "application/json"
			},
			"content": read_file("tasks.json")
		}
	elif path.startswith("/complete/"):
		taskid = path[10:]
		f = json.loads(read_file("tasks.json"))
		f[int(taskid)]["repeat"] = 0
		write_file("tasks.json", json.dumps(f, sort_keys=True, indent=4).replace("    ", "\t"))
		return {
			"status": 200,
			"headers": {},
			"content": ""
		}
	elif path.startswith("/restore/"):
		taskid = path[9:]
		f = json.loads(read_file("tasks.json"))
		f[int(taskid)]["repeat"] = 1
		write_file("tasks.json", json.dumps(f, sort_keys=True, indent=4).replace("    ", "\t"))
		return {
			"status": 200,
			"headers": {},
			"content": ""
		}
	else:
		return {
			"status": 404,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": f"<html><head><title>Task Manager</title></head>\n<body>\n\
<h1>Not Found</h1><p><a href='/' style='color: rgb(0, 0, 238);'>Return home</a></p>\
\n</body></html>"
		}

class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
		res = get(self.path)
		self.send_response(res["status"])
		for h in res["headers"]:
			self.send_header(h, res["headers"][h])
		self.end_headers()
		self.wfile.write(res["content"].encode("utf-8"))
		#self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
		#self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
		#self.wfile.write(bytes("<body>", "utf-8"))
		#self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
		#self.wfile.write(bytes("</body></html>", "utf-8"))
	def log_message(self, format: str, *args) -> None:
		print(args[0].split(" ")[0], "request to", args[0].split(" ")[1], "(status code:", args[1] + ")")
		# don't output requests

if __name__ == "__main__":
	webServer = HTTPServer((hostName, serverPort), MyServer)
	print("Server started http://%s:%s" % (hostName, serverPort))
	try:
		webServer.serve_forever()
	except KeyboardInterrupt:
		pass
	webServer.server_close()
	print("Server stopped.")
