from datetime import datetime
import os
import re
from typing import List, Optional
from core.log_entry import LogEntry


class LogParser:
    
    LOG_PATTERN = r'\[(.+?)\] \[(\w+)\] (.+)'
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


    def parse_files(self, file_paths: List[str]) -> List[LogEntry]:
        all_entries = []
        for file_path in file_paths:
            entries = self.parse_file(file_path)
            all_entries.extend(entries)
        
        # Sort by timestamp
        return sorted(all_entries, key=lambda x: x.timestamp)


    def parse_file(self, file_path: str) -> List[LogEntry]:
        entries = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    entry = self.parse_line(line, file_path, line_num)
                    if entry:
                        entries.append(entry)
        except Exception as e:
            raise Exception(f"Error reading {file_path}: {str(e)}")
        
        return entries


    def parse_line(self, line: str, file_path: str, line_num: int) -> Optional[LogEntry]:
        line = line.rstrip('\n')
        if not line.strip():
            return None
            
        match = re.match(self.LOG_PATTERN, line)
        if match:
            try:
                timestamp = datetime.strptime(match.group(1), self.TIME_FORMAT)
                return LogEntry(
                    timestamp=timestamp,
                    level=match.group(2).lower(),
                    message=match.group(3),
                    file_name=os.path.basename(file_path),
                    file_path=file_path,
                    line_number=line_num,
                    raw=line
                )
            except ValueError:
                return None
        return None    