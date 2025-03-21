import tornado.ioloop
import tornado.web
import tornado.websocket
from handlers import ChatWebSocketHandler


def make_app():
    """Create a Tornado web application with WebSocket handler."""
    return tornado.web.Application([
        (r"/ws/chat", ChatWebSocketHandler),  # Route for WebSocket connections
    ])

if __name__ == "__main__":
    # Create the Tornado application
    app = make_app()
    # Listen on port 8888 for incoming connections
    app.listen(8888)
    print("Tornado server started on port 8888")
    # Start the Tornado I/O loop to handle events
    tornado.ioloop.IOLoop.current().start()
