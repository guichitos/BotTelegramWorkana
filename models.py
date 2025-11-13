# models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Project:
    Title: str
    Description: Optional[str]
    Url: str
