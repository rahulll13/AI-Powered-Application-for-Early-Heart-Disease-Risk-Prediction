import subprocess
import os
import sys
import time

def main():
    """
    Starts both the Flask backend and the frontend http.server in parallel
    from a single terminal.
    """
    project_root = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(project_root, 'frontend')

    # --- Get the current Python executable ---
    # This is the robust way to find Python, both locally and in deployment.
    # It avoids hardcoding 'venv' paths.
    python_executable = sys.executable 

    # --- Start the Flask Backend Server ---
    print("--- Starting Flask Backend Server (on http://127.0.0.1:5000) ---")
    backend_env = os.environ.copy()
    backend_env['FLASK_APP'] = 'run.py'
    
    # Use 'python -m flask run' instead of calling the 'flask' executable directly
    backend_process = subprocess.Popen(
        [python_executable, '-m', 'flask', 'run'], 
        cwd=project_root, 
        env=backend_env
    )
    
    # Give the backend a moment to start up
    time.sleep(2)

    # --- Start the Frontend HTTP Server ---
    print("\n--- Starting Frontend HTTP Server (on http://localhost:8000) ---")
    
    # Use 'python -m http.server'
    frontend_process = subprocess.Popen(
        [python_executable, '-m', 'http.server'], 
        cwd=frontend_dir
    )
    
    print("\nServers are running. Press CTRL+C in this terminal to shut them both down.")

    try:
        # Wait for the processes to complete. They will run until you stop them.
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        # --- Handle shutdown ---
        print("\n--- Shutting down servers ---")
        backend_process.terminate()
        frontend_process.terminate()
        print("Servers have been shut down.")

if __name__ == "__main__":
    main()
