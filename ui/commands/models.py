from dataclasses import dataclass, field
from typing import Optional, Any, List

@dataclass
class CommandResult:
    """Результат выполнения команды"""
    success: bool
    message: str
    data: Optional[Any] = None

@dataclass
class CommandContext:
    """Контекст выполнения команды"""
    current_user_id: Optional[int] = None
    args: List[str] = field(default_factory=list)
