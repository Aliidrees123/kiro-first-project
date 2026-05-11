"""Task dataclass definition."""

import uuid
from dataclasses import dataclass, field


@dataclass
class Task:
    title: str
    done: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
