"""
Utility module for scanning and detecting virtual environment folders.
"""
import os
import time
from typing import List, Dict, Optional


def get_folder_size(folder_path: str) -> float:
    """
    Calculate the total size of a folder in megabytes.
    
    Args:
        folder_path (str): Path to the folder to measure.
    
    Returns:
        float: Size of the folder in MB.
    
    Raises:
        OSError: If there's an error accessing the folder.
    """
    total_bytes = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):
                try:
                    total_bytes += os.path.getsize(file_path)
                except (OSError, IOError):
                    # Skip files that can't be accessed
                    continue
    return total_bytes / (1024 * 1024)


def get_venv_age_days(venv_path: str) -> float:
    """
    Calculate the age of a venv folder in days since last modification.
    
    Args:
        venv_path (str): Path to the venv folder.
    
    Returns:
        float: Age in days since last modification.
    
    Raises:
        OSError: If there's an error accessing the folder.
    """
    last_modified = os.path.getmtime(venv_path)
    age_seconds = time.time() - last_modified
    return age_seconds / (60 * 60 * 24)


def scan_for_venvs(root_dir: str, days_unused: int = 60, min_size_mb: int = 200) -> List[Dict[str, any]]:
    """
    Scan a directory tree for virtual environment folders matching criteria.
    
    Args:
        root_dir (str): Root directory to start scanning from.
        days_unused (int): Minimum age in days for venvs to be included.
        min_size_mb (int): Minimum size in MB for venvs to be included.
    
    Returns:
        List[Dict]: List of dictionaries containing venv information:
            - venv_path: Full path to the venv folder
            - project_path: Path to the parent project folder
            - project_name: Name of the project folder
            - age_days: Age in days since last modification
            - size_mb: Size in megabytes
            - meets_criteria: Boolean indicating if it meets deletion criteria
    
    Raises:
        ValueError: If root_dir doesn't exist or is not a directory.
    """
    if not os.path.exists(root_dir):
        raise ValueError(f"Root directory does not exist: {root_dir}")
    
    if not os.path.isdir(root_dir):
        raise ValueError(f"Root path is not a directory: {root_dir}")
    
    venv_list = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Check if 'venv' folder exists in current directory
        if "venv" in dirnames:
            venv_path = os.path.join(dirpath, "venv")
            project_path = dirpath
            project_name = os.path.basename(dirpath)
            
            try:
                age_days = get_venv_age_days(venv_path)
                size_mb = get_folder_size(venv_path)
                meets_criteria = (age_days > days_unused) and (size_mb > min_size_mb)
                
                venv_info = {
                    "venv_path": venv_path,
                    "project_path": project_path,
                    "project_name": project_name,
                    "age_days": age_days,
                    "size_mb": size_mb,
                    "meets_criteria": meets_criteria
                }
                
                venv_list.append(venv_info)
                
            except Exception as e:
                # Log error but continue scanning
                print(f"Error scanning {venv_path}: {e}")
                continue
    
    return venv_list


def filter_venvs_by_criteria(venv_list: List[Dict], days_unused: int, min_size_mb: int) -> List[Dict]:
    """
    Filter a list of venvs based on age and size criteria.
    
    Args:
        venv_list (List[Dict]): List of venv information dictionaries.
        days_unused (int): Minimum age in days.
        min_size_mb (int): Minimum size in MB.
    
    Returns:
        List[Dict]: Filtered list containing only venvs meeting the criteria.
    """
    filtered_list = []
    for venv_info in venv_list:
        if venv_info["age_days"] > days_unused and venv_info["size_mb"] > min_size_mb:
            filtered_list.append(venv_info)
    return filtered_list
