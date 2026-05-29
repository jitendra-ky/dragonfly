import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken, UntypedToken

User = get_user_model()

# Dictionary to keep track of user connections
connections: dict[str, "ChatConsumer"] = {}


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        """Open a new WebSocket connection with JWT authentication."""
        try:
            token = self.scope["query_string"].decode()
            # Parse token= from query string
            token_param = None
            for part in token.split("&"):
                if part.startswith("token="):
                    token_param = part[len("token="):]
                    break

            if not token_param:
                await self.close(code=4001)
                return

            try:
                UntypedToken(token_param)
                access_token = AccessToken(token_param)
                user_id = access_token["user_id"]

                try:
                    user = await User.objects.aget(id=user_id)
                    if not user.is_active:
                        await self.close(code=4003)
                        return
                except User.DoesNotExist:
                    await self.close(code=4004)
                    return

                self.user_id = str(user_id)
                connections[self.user_id] = self
                await self.accept()
                print(f"WebSocket connection opened for user {self.user_id}")

            except (InvalidToken, TokenError) as e:
                print(f"Invalid token: {e!s}")
                await self.close(code=4002)
                return

        except Exception as e:
            print(f"WebSocket authentication error: {e!s}")
            await self.close(code=4000)
            return

    async def disconnect(self, _close_code: int) -> None:
        """Close the WebSocket connection."""
        if hasattr(self, "user_id") and self.user_id in connections:
            del connections[self.user_id]
            print(f"WebSocket connection closed for user {self.user_id}")

    async def receive(self, text_data: str) -> None:
        """Receive a message from the client and forward it to the recipient."""
        data = json.loads(text_data)
        sender = data.get("sender")
        receiver = data.get("receiver")
        content = data.get("content")

        if receiver in connections:
            await connections[receiver].send(text_data=json.dumps({
                "sender": sender,
                "receiver": receiver,
                "content": content,
            }))
