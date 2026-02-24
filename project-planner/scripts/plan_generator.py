import os
import sys
import argparse
from llm import LLMClient

def get_multiline_input(prompt_text):
    print(prompt_text)
    print("(Enter an empty line to finish)")
    lines = []
    while True:
        line = input()
        if not line.strip():
            break
        lines.append(line)
    return "\n".join(lines)

def ask_clarifying_questions(llm, idea, num_questions=3):
    context = f"Initial Idea: {idea}\n"
    for i in range(num_questions):
        prompt = f"""
You are an expert AI project manager. We are defining the scope and development direction for a new project.
Here is the context of the project so far:
{context}

Based on this context, ask EXACTLY ONE critical question to the user to clarify their development direction, technical preferences, or project scope. 
Do not ask multiple questions. Just ask the single most important question right now.
"""
        print(f"\n[AI] Generating question {i+1} of {num_questions}...")
        question = llm.generate_response(prompt).strip()
        print(f"\n==================================================")
        print(f"🤖 Question {i+1} of {num_questions}")
        print(f"==================================================")
        answer = get_multiline_input(f"{question}\n\n👉 Your answer:")
        if not answer.strip():
            print("Skipped.")
            continue
        context += f"\nQ{i+1}: {question}\nA{i+1}: {answer}\n"
    return context

def generate_options(llm, context):
    prompt = f"""
You are an expert AI project manager. The user wants to build a project with the following context:
"{context}"

Please provide 3 distinct, high-level structural approaches (options) for how to plan this project's development milestones. 
For example, the options could vary by scope (e.g., MVP vs. Full-Featured), methodology (e.g., Frontend-first vs Backend-first), or speed (Fast-track vs Thorough).

Format your response exactly like this, and do not include any other conversational text:

[Option 1: Name of Option 1]
Description highlighting the pros/cons and focus of this approach.

[Option 2: Name of Option 2]
Description highlighting the pros/cons and focus of this approach.

[Option 3: Name of Option 3]
Description highlighting the pros/cons and focus of this approach.
"""
    print("\n[AI] Generating project plan options based on your idea...\n")
    return llm.generate_response(prompt)

def generate_todo(llm, context, chosen_option):
    prompt = f"""
You are an expert AI software architect and project manager. The user wants to build a project with the following context:
"{context}"

The user has selected the following approach for the project plan:
"{chosen_option}"

Generate a highly detailed, phase-based project task list in Markdown format. 
The output MUST follow this exact structure, using Phases, Weeks, and Specific Tasks.
Use deep technical context and be as specific as possible. Do not output anything except the markdown content.

# [Project Name] Detailed Todo List
> [Brief description of the project goal based on the chosen option]

---

## 📋 Phase 1: [Phase Name] (Week 1-X)
### Week 1: [Week Goal]
#### 1.1 [Category - e.g., UI Components]
- [ ] [Specific Task 1]
- [ ] [Specific Task 2]
  ```bash
  # Optional command or code snippet context
  ```

#### 1.2 [Category - e.g., Logic & State]
- [ ] [Specific Task A]

... continue for all necessary phases, weeks, and tasks. Make sure the plan is comprehensive and ready for execution.
"""
    print("\n[AI] Generating detailed PROJECT_TODO.md... This might take a moment.\n")
    # Using a model with larger context window and better formatting capabilities if possible, but default is fine
    return llm.generate_response(prompt)

def main():
    parser = argparse.ArgumentParser(description="Intelligent Planning Automation for Antigravity Workspace")
    parser.add_argument("--idea", type=str, help="The core idea or PRD of the project")
    parser.add_argument("--provider", type=str, default="gemini", choices=["gemini", "anthropic"], help="LLM provider")
    parser.add_argument("--output", type=str, default="PROJECT_TODO.md", help="Output markdown file path")
    args = parser.parse_args()

    try:
        llm = LLMClient(provider=args.provider)
    except ValueError as e:
        print(f"Error: {e}")
        print("Please export LLM_API_KEY before running this script.")
        sys.exit(1)

    print("==================================================")
    print("🚀 Project Planner: Intelligent Automation")
    print("==================================================\n")

    idea = args.idea
    if not idea:
        idea = get_multiline_input("💡 What do you want to build? Briefly describe your project idea or PRD:")

    if not idea.strip():
        print("No idea provided. Exiting.")
        sys.exit(0)

    print("\n==================================================")
    print("🧠 Let's clarify the development direction (3 questions)...")
    print("==================================================")
    context = ask_clarifying_questions(llm, idea, num_questions=3)

    options_text = generate_options(llm, context)
    print("==================================================")
    print("✨ Here are 3 potential approaches for your project:")
    print("==================================================")
    print(options_text)
    print("==================================================")
    
    choice = input("👉 Which option do you prefer? (1, 2, or 3, or 'q' to quit): ").strip().lower()
    
    if choice == 'q':
        print("Exiting.")
        sys.exit(0)
    
    # Extract the chosen option text to send back to the LLM
    try:
        choice_idx = int(choice)
        if choice_idx not in [1, 2, 3]:
            raise ValueError
    except ValueError:
        print("Invalid choice. Please run the script again.")
        sys.exit(1)

    # Simple parsing to get the selected option block
    options_blocks = options_text.split("[Option ")
    chosen_option_context = ""
    for block in options_blocks:
        if block.startswith(f"{choice_idx}:"):
            chosen_option_context = f"[Option {block.strip()}"
            break
            
    if not chosen_option_context:
        chosen_option_context = f"The user selected Option {choice_idx} from the provided list."

    todo_markdown = generate_todo(llm, context, chosen_option_context)
    
    # Clean up standard Markdown fences if the LLM added them
    if todo_markdown.startswith("```markdown"):
        todo_markdown = todo_markdown[11:].strip()
        if todo_markdown.endswith("```"):
            todo_markdown = todo_markdown[:-3].strip()

    try:
        with open(args.output, "w") as f:
            f.write(todo_markdown)
        print("==================================================")
        print(f"✅ Success! Detailed plan generated at: {args.output}")
        print("==================================================")
    except Exception as e:
        print(f"Failed to write output file: {e}")

if __name__ == "__main__":
    main()
