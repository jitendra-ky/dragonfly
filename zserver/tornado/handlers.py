import json

import tornado.websocket


class ChatWebSocketHandler(tornado.websocket.WebSocketHandler):
    # Dictionary to keep track of user connections
    connections = {}

    def open(self) -> None:
        """Open a new WebSocket connection."""
        user_id = self.get_argument("user_id")
        self.connections[user_id] = self
        print(f"WebSocket connection opened for user {user_id}")

    def on_message(self, message: str) -> None:
        """Receive a message from the client."""
        data = json.loads(message)
        sender = data.get("sender")
        receiver = data.get("receiver")
        content = data.get("content")

        # Send the message to the intended recipient
        if receiver in self.connections:
            self.connections[receiver].write_message(json.dumps({
                "sender": sender,
                "receiver": receiver,
                "content": content,
            }))

    def on_close(self) -> None:
        """Close the WebSocket connection."""
        user_id = self.get_argument("user_id")
        if user_id in self.connections:
            del self.connections[user_id]
        print(f"WebSocket connection closed for user {user_id}")

    def check_origin(self, origin: str) -> bool:
        """Allow connections from any origin."""
        print(f"Origin: {origin}")
        return True
