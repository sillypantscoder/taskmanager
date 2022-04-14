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
	elif path.startswith("/edit/"):
		taskid = path[6:]
		f = json.loads(read_file("tasks.json"))
		file = read_file("edit.html").replace("{TASKID}", taskid).replace("{TASKNAME}", f[int(taskid)]["name"]).replace("{TASKDATEISO}", f[int(taskid)]["date"])
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": file
		}
	elif path == "/new":
		f = json.loads(read_file("tasks.json"))
		f.append({
			"name": "Enter task name here",
			"date": "",
			"repeat": 1
		})
		write_file("tasks.json", json.dumps(f, sort_keys=True, indent=4).replace("    ", "\t"))
		return {
			"status": 307,
			"headers": {
				"Location": "/edit/" + str(len(f) - 1)
			},
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

def post(path, headers):
	if path.startswith("/post_edit/"):
		taskid = path[11:]
		f = json.loads(read_file("tasks.json"))
		f[int(taskid)]["name"] = headers["X-Task-Name"]
		f[int(taskid)]["date"] = headers["X-Task-Date"]
		f[int(taskid)]["repeat"] = int(headers["X-Task-Repeat"])
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
	def do_POST(self):
		res = post(self.path, self.headers)
		self.send_response(res["status"])
		for h in res["headers"]:
			self.send_header(h, res["headers"][h])
		self.end_headers()
		self.wfile.write(res["content"].encode("utf-8"))
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
