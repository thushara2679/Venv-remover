"""
Utility module for deleting virtual environment folders.
"""
import os
import shutil
from typing import List, Dict, Tuple, Any


def delete_venv(venv_path: str, dry_run: bool = True) -> Tuple[bool, str]:
    """
    Delete a virtual environment folder.
    
    Args:
        venv_path (str): Full path to the venv folder to delete.
        dry_run (bool): If True, simulate deletion without actually deleting.
    
    Returns:
        Tuple[bool, str]: (success_status, message)
            - success_status: True if deletion succeeded (or would succeed in dry run)
            - message: Description of the result
    
    Raises:
        ValueError: If venv_path is empty or invalid.
    """
    if not venv_path or not venv_path.strip():
        raise ValueError("venv_path cannot be empty")
    
    if not os.path.exists(venv_path):
        return False, f"Path does not exist: {venv_path}"
    
    if not os.path.isdir(venv_path):
        return False, f"Path is not a directory: {venv_path}"
    
    if dry_run:
        return True, f"[DRY RUN] Would delete: {venv_path}"
    
    try:
        shutil.rmtree(venv_path)
        return True, f"Successfully deleted: {venv_path}"
    except PermissionError as e:
        return False, f"Permission denied: {venv_path} - {str(e)}"
    except Exception as e:
        return False, f"Error deleting {venv_path}: {str(e)}"


def delete_multiple_venvs(venv_paths: List[str], dry_run: bool = True) -> Dict[str, Any]:
    """
    Delete multiple virtual environment folders.
    
    Args:
        venv_paths (List[str]): List of venv folder paths to delete.
        dry_run (bool): If True, simulate deletion without actually deleting.
    
    Returns:
        Dict containing:
            - total: Total number of venvs attempted
            - successful: Number of successful deletions
            - failed: Number of failed deletions
            - results: List of tuples (venv_path, success, message)
    """
    results = []
    successful = 0
    failed = 0
    
    for venv_path in venv_paths:
        success, message = delete_venv(venv_path, dry_run)
        results.append((venv_path, success, message))
        
        if success:
            successful += 1
        else:
            failed += 1
    
    return {
        "total": len(venv_paths),
        "successful": successful,
        "failed": failed,
        "results": results
    }


def calculate_space_freed(venv_list: List[Dict]) -> float:
    """
    Calculate total space that would be freed by deleting venvs.
    
    Args:
        venv_list (List[Dict]): List of venv information dictionaries.
    
    Returns:
        float: Total size in MB that would be freed.
    """
    total_mb = 0.0
    for venv_info in venv_list:
        total_mb += venv_info.get("size_mb", 0.0)
    return total_mb
