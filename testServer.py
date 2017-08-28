from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


def webServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith('/hello'):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_header()

                output = ""
                output += "<html><body>Hello!</body></html>"
                self.wfile.write(output)
                print(output)
                return
        except Exception as e:
            self.send_error(404, "File Not Found " + self.path)


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print('Web Server running on port : ', port)
        server.server_forever()
    except KeyboardInterrupt:
    	print ("^C Enterred, Stooping web server.")
    	server.socket.close()	


if __name__ == 'main':
	main()
