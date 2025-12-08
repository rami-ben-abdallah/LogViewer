from dataclasses import dataclass
from datetime import datetime

@dataclass
class LogEntry:
    timestamp: datetime
    level: str
    message: str
    file_name: str
    file_path: str
    line_number: int
    raw: str
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'message': self.message,
            'file': self.file_name,
            'line_number': self.line_number
        }