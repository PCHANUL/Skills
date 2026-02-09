import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='Generate a detailed, phase-structured task list template.')
    parser.add_argument('--output', type=str, required=True, help='The output markdown file path.')
    parser.add_argument('--title', type=str, required=True, help='Title of the project or module.')
    parser.add_argument('--description', type=str, default='Comprehensive task list for project execution.', help='Brief description of the project goal.')
    parser.add_argument('--phases', type=int, default=3, help='Number of major development phases.')
    parser.add_argument('--weeks', type=int, default=4, help='Number of weeks per phase.')

    args = parser.parse_args()

    content = f"""# {args.title} Detailed Todo List

> {args.description}

---
"""

    week_number = 1
    for phase_idx in range(1, args.phases + 1):
        # Calculate week range for this phase
        start_week = week_number
        end_week = week_number + args.weeks - 1
        
        content += f"\n## 📋 Phase {phase_idx}: [Phase {phase_idx} Name] (Week {start_week}-{end_week})\n"
        
        for w in range(args.weeks):
            content += f"\n### Week {week_number}: [Week {week_number} Goal]\n"
            
            # Add placeholders for detailed tasks
            content += f"\n#### {week_number}.1 [Category 1 - e.g., UI Components]\n"
            content += f"- [ ] [Specific Task 1]\n"
            content += f"  ```bash\n  # Optional command or snippet\n  ```\n"
            content += f"- [ ] [Specific Task 2]\n"
            
            content += f"\n#### {week_number}.2 [Category 2 - e.g., Logic & State]\n"
            content += f"- [ ] [Detailed Task A]\n"
            content += f"- [ ] [Detailed Task B]\n"
            
            content += f"\n#### {week_number}.3 [Category 3 - e.g., Testing & Polish]\n"
            content += f"- [ ] [Unit Test Implementation]\n"
            content += f"- [ ] [Manual Verification]\n"

            week_number += 1
        
        content += "\n---\n"

    try:
        with open(args.output, 'w') as f:
            f.write(content)
        print(f"Detailed task list template generated at: {args.output}")
        print(f"Review the file to fill in specific [Placeholders].")
    except Exception as e:
        print(f"Error generating template: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
