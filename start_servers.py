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

    # --- Determine the correct executables based on the OS ---
    if sys.platform == "win32":
        venv_python = os.path.join(project_root, 'venv', 'Scripts', 'python.exe')
        flask_executable = os.path.join(project_root, 'venv', 'Scripts', 'flask.exe')
    else: # macOS, Linux
        venv_python = os.path.join(project_root, 'venv', 'bin', 'python')
        flask_executable = os.path.join(project_root, 'venv', 'bin', 'flask')

    # --- Start the Flask Backend Server ---
    print("--- Starting Flask Backend Server (on http://127.0.0.1:5000) ---")
    backend_env = os.environ.copy()
    backend_env['FLASK_APP'] = 'run.py'
    # Popen starts the process in the background
    backend_process = subprocess.Popen([flask_executable, 'run'], cwd=project_root, env=backend_env)
    
    # Give the backend a moment to start up
    time.sleep(2)

    # --- Start the Frontend HTTP Server ---
    print("\n--- Starting Frontend HTTP Server (on http://localhost:8000) ---")
    # Popen also starts this process in the background
    frontend_process = subprocess.Popen([venv_python, '-m', 'http.server'], cwd=frontend_dir)
    
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