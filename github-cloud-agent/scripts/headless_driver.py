import argparse
import sys
import subprocess
import os

# Relative import (if part of skill module)
# from .llm_client import LLMClient

def apply_change_to_file(file_path, new_content):
    """
    Applies the change. Simplistic: overwrites or replaces whole file. 
    Ideally, use `sed` or diff parsing if available.
    """
    with open(file_path, 'w') as f:
        f.write(new_content)
    print(f"Applied change to {file_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", required=True)
    parser.add_argument("--comment", required=True)
    args = parser.parse_args()
    
    # 1. Parse Comment
    instruction = args.comment.replace("/agent ", "").strip()
    print(f"Received instruction: {instruction}")

    # 2. Read Repo Context
    # (Simplified: Just read README or specific file mentioned in instruction if possible)
    # Ideally, search for relevant files.
    
    # 3. Call LLM
    try:
        # sys.path.append(os.path.dirname(__file__))
        from llm_client import LLMClient
        client = LLMClient(provider="gemini") # Default provider
        
        prompt = f"""
        You are a coding agent.
        Instruction: {instruction}
        
        Repo structure: (Run `ls -R` or similar here if needed)
        
        Please provide the full content of the file that needs to be created or modified.
        Format your response as:
        FILE: <path/to/file>
        CONTENT:
        <code here>
        END_CONTENT
        """
        
        print("Thinking...")
        response = client.generate_response(prompt)
        print("Response received.")
        
        # 4. Parse Response & Apply
        lines = response.splitlines()
        current_file = None
        content_lines = []
        parsing_content = False
        
        for line in lines:
            if line.startswith("FILE: "):
                current_file = line.replace("FILE: ", "").strip()
            elif line.startswith("CONTENT:"):
                parsing_content = True
            elif line.startswith("END_CONTENT"):
                parsing_content = False
                if current_file:
                    apply_change_to_file(current_file, "\n".join(content_lines))
                    content_lines = []
                    current_file = None
            elif parsing_content:
                content_lines.append(line)
                
    except Exception as e:
        print(f"Agent failed: {e}")
        sys.exit(1)

    # 5. Commit and PR
    branch_name = f"agent/fix-issue-{args.issue}"
    subprocess.run(["git", "checkout", "-b", branch_name])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"Agent fix for issue #{args.issue}"])
    subprocess.run(["git", "push", "origin", branch_name])
    
    # Create PR logic (gh pr create)
    # ...

if __name__ == "__main__":
    main()
