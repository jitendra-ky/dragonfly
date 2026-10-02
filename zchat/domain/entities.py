from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Message:
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime
