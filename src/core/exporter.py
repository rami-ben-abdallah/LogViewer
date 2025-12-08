import json
from datetime import datetime
from typing import List

from core.log_entry import LogEntry

def export_to_json(entries : List[LogEntry], file_path, metadata=None):
    export_data = {
        'metadata': metadata or {
            'export_time': datetime.now().isoformat(),
            'entry_count': len(entries)
        },
        'entries': [entry.to_dict() for entry in entries]
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2)
    
    return True

def export_to_txt(entries, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("EXPORTED LOG ENTRIES\n")
        f.write("=" * 80 + "\n")
        
        for entry in entries:
            entry_dict = entry.to_dict()
            f.write(f"[{entry_dict['timestamp']}] [{entry_dict['level']:7}] ")
            f.write(f"{entry_dict['message']} (Line {entry_dict['line_number']})\n")
    
    return True