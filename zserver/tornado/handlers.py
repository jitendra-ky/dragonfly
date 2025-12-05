import json

import tornado.websocket
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken, UntypedToken

User = get_user_model()


class ChatWebSocketHandler(tornado.websocket.WebSocketHandler):
    # Dictionary to keep track of user connections
    connections = {}

    def open(self) -> None:
        """Open a new WebSocket connection with JWT authentication."""
        try:
            # Get JWT token from query parameter
            token = self.get_argument("token", None)

            if not token:
                self.close(code=4001, reason="Authentication token required")
                return

            # Validate JWT token
            try:
                # Decode and validate the token
                UntypedToken(token)

                # Extract user_id from token
                access_token = AccessToken(token)
                user_id = access_token["user_id"]

                # Verify user exists
                try:
                    user = User.objects.get(id=user_id)
                    if not user.is_active:
                        self.close(code=4003, reason="User is not active")
                        return
                except User.DoesNotExist:
                    self.close(code=4004, reason="User not found")
                    return

                # Store connection with user_id
                self.user_id = str(user_id)
                self.connections[self.user_id] = self
                print(f"WebSocket connection opened for user {self.user_id}")

            except (InvalidToken, TokenError) as e:
                self.close(code=4002, reason=f"Invalid token: {e!s}")
                return

        except Exception as e:
            print(f"WebSocket authentication error: {e!s}")
            self.close(code=4000, reason="Authentication failed")
            return

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
        if hasattr(self, "user_id") and self.user_id in self.connections:
            del self.connections[self.user_id]
            print(f"WebSocket connection closed for user {self.user_id}")

    def check_origin(self, origin: str) -> bool:
        """Allow connections from any origin."""
        print(f"Origin: {origin}")
        return True
