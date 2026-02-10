import argparse
import subprocess
import sys
import os

# Maximum number of automated retry attempts
MAX_RETRIES = 3

def run_command(cmd_str):
    """Runs a shell command and returns (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd_str, 
            shell=True, 
            capture_output=True, 
            text=True
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def debug_loop(command):
    print(f"--- Self-Healing Debugger: Analyzing '{command}' ---")
    
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n[Attempt {attempt}/{MAX_RETRIES}] Running command...")
        
        code, out, err = run_command(command)
        
        if code == 0:
            print("✅ Command succeeded!")
            return 0
        
        print(f"❌ Command failed with exit code {code}.")
        print("--- Failure Output ---")
        # Print last 20 lines of error to avoid spam, or full if short
        err_lines = err.strip().splitlines()
        if not err_lines:
            err_lines = out.strip().splitlines() # sometimes error is in stdout
            
        print("\n".join(err_lines[-20:]))
        print("----------------------")
        
        # Here is where the Agentic Magic happens.
        # Since this script runs in the environment, it can't directly "think".
        # It needs to delegate the thinking to the Agent (User).
        
        print(f"\n!!! DEBUGGER ALERT: Attempt {attempt} Failed !!!")
        print("AGENT: Please analyze the error above and FIX the code now.")
        print("Use `view_file`, `replace_file_content` tools to fix the issue.")
        
        # Interactive pause for the agent to fix
        user_input = input("Press Enter after applying a fix (or 'q' to give up): ")
        if user_input.lower() == 'q':
            print("Debugging aborted by user.")
            return code

    print(f"\n❌ Failed to fix after {MAX_RETRIES} attempts.")
    return 1

def main():
    parser = argparse.ArgumentParser(description='Run a command with iterative debugging.')
    parser.add_argument('--command', type=str, required=True, help='The command to debug (e.g., "npm test")')
    
    args = parser.parse_args()
    
    exit_code = debug_loop(args.command)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
