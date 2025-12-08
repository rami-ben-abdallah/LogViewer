from datetime import datetime
from typing import List, Optional

from core.log_entry import LogEntry


class LogFilter:
   
    def apply(self, 
              entries: List[LogEntry],
              levels: Optional[List[str]] = None,
              time_from: Optional[datetime] = None,
              time_to: Optional[datetime] = None,
              search_text: Optional[str] = None) -> List[LogEntry]:
        filtered = []
        
        for entry in entries:
            if levels and entry.level not in levels:
                continue
            
            if time_from and entry.timestamp < time_from:
                continue

            if time_to and entry.timestamp > time_to:
                continue
            
            if search_text and search_text.lower() not in entry.message.lower():
                continue
            
            filtered.append(entry)
        
        return filtered