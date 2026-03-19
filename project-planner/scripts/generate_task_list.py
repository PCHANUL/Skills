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
>
> This file is intended to be issue-ready. Assume each week may be assigned to a different implementer.
> Each week section should contain enough context to execute without prior conversation history.

---

## How To Use This Document

- Before implementing a week, read the documents listed under `Read first`.
- Update both the code and the plan if the current code reality has changed.
- Do not leave a week without `Definition of done` and `Verification`.

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
            content += "\n**Why this week exists**\n"
            content += "- [Explain why this week matters in the overall plan]\n"
            content += "\n**Read first**\n"
            content += "- `[spec/doc/path.md]`\n"
            content += "- `[architecture/doc/path.md]`\n"
            content += "\n**Current code reality**\n"
            content += "- [Describe what currently exists and what is still wrong, missing, or legacy]\n"
            content += "\n**Target outcome**\n"
            content += "- [Describe what must be true when this week is complete]\n"

            content += f"\n#### {week_number}.1 [Category 1 - e.g., Contracts / Schema / Models]\n"
            content += "- [ ] [Specific Task 1]\n"
            content += "- [ ] [Specific Task 2]\n"

            content += f"\n#### {week_number}.2 [Category 2 - e.g., Business Logic / Services]\n"
            content += "- [ ] [Detailed Task A]\n"
            content += "- [ ] [Detailed Task B]\n"

            content += f"\n#### {week_number}.3 [Category 3 - e.g., UI / Testing / Migration]\n"
            content += "- [ ] [Detailed Task C]\n"
            content += "- [ ] [Detailed Task D]\n"

            content += "\n**Files likely touched**\n"
            content += "- `[path/to/file]`\n"
            content += "- `[path/to/another-file]`\n"

            content += "\n**Out of scope**\n"
            content += "- [Clarify what this week should not try to solve]\n"

            content += "\n**Definition of done**\n"
            content += "- [Observable completion criterion 1]\n"
            content += "- [Observable completion criterion 2]\n"

            content += "\n**Verification**\n"
            content += "- `[command to run]`\n"
            content += "- [Manual verification scenario]\n"

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
