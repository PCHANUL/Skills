
import re
import sys

def parse_markdown(file_path):
    """Parses the task list markdown file into a structured dictionary."""
    phases = []
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found {file_path}")
        sys.exit(1)

    current_phase = None
    current_week = None
    
    print(f"Parsing file: {file_path}")
    
    for line in lines:
        line = line.strip()
        
        # Match Phase: "## 📋 Phase 1: Phase Name (Week 1-4)"
        # Regex adjustment to match emojis and extra spaces if needed
        phase_match = re.match(r'^##\s+.*?Phase\s+(\d+):\s+(.*)', line)
        if phase_match:
            if current_phase:
                phases.append(current_phase)
            
            phase_num = phase_match.group(1)
            phase_title = phase_match.group(2)
            current_phase = {
                'number': phase_num,
                'title': f"Phase {phase_num}: {phase_title}",
                'weeks': []
            }
            current_week = None
            print(f"Found Phase {phase_num}: {phase_title}")
            continue
            
        # Match Week: "### Week 1: Week Goal"
        week_match = re.match(r'^###\s+Week\s+(\d+):\s+(.*)', line)
        if week_match:
            if current_phase:
                week_num = week_match.group(1)
                week_goal = week_match.group(2)
                current_week = {
                    'number': week_num,
                    'title': f"Week {week_num}: {week_goal}",
                    'body': f"# Week {week_num} Tasks\n\n"
                }
                current_phase['weeks'].append(current_week)
                print(f"  Found Week {week_num}: {week_goal}")
            continue
            
    if current_phase:
        phases.append(current_phase)
        
    return phases

if __name__ == "__main__":
    phases = parse_markdown(sys.argv[1])
    print(f"\nTotal Phases Found: {len(phases)}")
    for p in phases:
        print(f"- {p['title']} ({len(p['weeks'])} weeks)")
