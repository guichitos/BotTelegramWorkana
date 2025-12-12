# models.py
from dataclasses import dataclass, field
from typing import List, Optional, TypedDict


class Skill(TypedDict, total=False):
    name: str
    slug: str
    href: str

@dataclass
class Project:
    Title: str
    Description: Optional[str]
    Url: str
    Skills: List[Skill] = field(default_factory=list)
