from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class Prompt:
    """Model: Represents a prompt entity."""

    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    content: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
