"""
Utility module for generating requirements.txt from virtual environments.
"""
import os
import subprocess
from typing import Tuple, Optional


def get_venv_python_path(venv_path: str) -> Optional[str]:
    """
    Get the Python executable path within a venv.
    
    Args:
        venv_path (str): Path to the venv folder.
    
    Returns:
        Optional[str]: Path to Python executable, or None if not found.
    """
    # Check Windows path
    python_exe = os.path.join(venv_path, "Scripts", "python.exe")
    if os.path.exists(python_exe):
        return python_exe
    
    # Check Unix/Linux path
    python_bin = os.path.join(venv_path, "bin", "python")
    if os.path.exists(python_bin):
        return python_bin
    
    return None


def generate_requirements_from_venv(venv_path: str, output_path: str, overwrite: bool = False) -> Tuple[bool, str]:
    """
    Generate requirements.txt from a virtual environment.
    
    Args:
        venv_path (str): Path to the venv folder.
        output_path (str): Path where requirements.txt should be saved.
        overwrite (bool): Whether to overwrite existing requirements.txt.
    
    Returns:
        Tuple[bool, str]: (success_status, message)
            - success_status: True if generation succeeded
            - message: Description of the result
    
    Raises:
        ValueError: If venv_path or output_path is empty.
    """
    if not venv_path or not venv_path.strip():
        raise ValueError("venv_path cannot be empty")
    
    if not output_path or not output_path.strip():
        raise ValueError("output_path cannot be empty")
    
    if not os.path.exists(venv_path):
        return False, f"Venv path does not exist: {venv_path}"
    
    if not os.path.isdir(venv_path):
        return False, f"Venv path is not a directory: {venv_path}"
    
    # Check if requirements.txt already exists
    if os.path.exists(output_path) and not overwrite:
        return False, f"Requirements file already exists: {output_path}"
    
    # Get Python executable from venv
    python_path = get_venv_python_path(venv_path)
    if not python_path:
        return False, f"Could not find Python executable in venv: {venv_path}"
    
    try:
        # Run pip freeze to get installed packages
        result = subprocess.run(
            [python_path, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return False, f"pip freeze failed: {result.stderr}"
        
        requirements_content = result.stdout
        
        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(requirements_content)
        
        # Count number of packages
        package_count = len([line for line in requirements_content.split("\n") if line.strip() and not line.startswith("#")])
        
        return True, f"Successfully created requirements.txt with {package_count} packages"
    
    except subprocess.TimeoutExpired:
        return False, "pip freeze timed out"
    except Exception as e:
        return False, f"Error generating requirements: {str(e)}"


def generate_requirements_for_multiple_venvs(venv_info_list: list, overwrite: bool = False) -> dict:
    """
    Generate requirements.txt for multiple venvs.
    
    Args:
        venv_info_list (list): List of venv info dictionaries containing:
            - venv_path: Path to venv
            - project_path: Path to project folder
        overwrite (bool): Whether to overwrite existing requirements files.
    
    Returns:
        dict: Results containing:
            - total: Total number of venvs
            - successful: Number of successful generations
            - failed: Number of failed generations
            - results: List of tuples (venv_path, success, message)
    """
    results = []
    successful = 0
    failed = 0
    
    for venv_info in venv_info_list:
        venv_path = venv_info.get("venv_path")
        project_path = venv_info.get("project_path")
        
        if not venv_path or not project_path:
            results.append((venv_path, False, "Missing venv_path or project_path"))
            failed += 1
            continue
        
        output_path = os.path.join(project_path, "requirements.txt")
        success, message = generate_requirements_from_venv(venv_path, output_path, overwrite)
        results.append((venv_path, success, message))
        
        if success:
            successful += 1
        else:
            failed += 1
    
    return {
        "total": len(venv_info_list),
        "successful": successful,
        "failed": failed,
        "results": results
    }
