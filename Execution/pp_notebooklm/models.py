from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class Notebook:
    id: str
    title: str
    source_count: int
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
    is_owned: bool = True

@dataclass
class Source:
    id: str
    notebook_id: str
    title: str
    type: str  # e.g., 'google_doc', 'pasted_text'
    char_count: int = 0

@dataclass
class Asset:
    id: str
    notebook_id: str
    type: str  # 'video', 'infographic', 'audio'
    status: str  # 'pending', 'completed', 'failed'
    url: Optional[str] = None
    created_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
