"""
Unit tests for venv_scanner utility module.
"""
import unittest
import os
import tempfile
import shutil
from utils.venv_scanner import (
    get_folder_size,
    get_venv_age_days,
    scan_for_venvs,
    filter_venvs_by_criteria
)


class TestVenvScanner(unittest.TestCase):
    """Test cases for venv scanner functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_project_dir = os.path.join(self.test_dir, "test_project")
        self.test_venv_dir = os.path.join(self.test_project_dir, "venv")
        
        # Create test directory structure
        os.makedirs(self.test_venv_dir, exist_ok=True)
        
        # Create a test file in venv
        test_file = os.path.join(self.test_venv_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Test content" * 1000)  # Create some content
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_get_folder_size(self):
        """Test folder size calculation."""
        size_mb = get_folder_size(self.test_venv_dir)
        self.assertGreater(size_mb, 0)
        self.assertIsInstance(size_mb, float)
    
    def test_get_venv_age_days(self):
        """Test venv age calculation."""
        age_days = get_venv_age_days(self.test_venv_dir)
        self.assertGreaterEqual(age_days, 0)
        self.assertIsInstance(age_days, float)
    
    def test_scan_for_venvs_valid_directory(self):
        """Test scanning for venvs in valid directory."""
        venv_list = scan_for_venvs(self.test_dir, days_unused=0, min_size_mb=0)
        self.assertIsInstance(venv_list, list)
        self.assertGreater(len(venv_list), 0)
        
        # Check structure of first result
        if venv_list:
            venv_info = venv_list[0]
            self.assertIn("venv_path", venv_info)
            self.assertIn("project_path", venv_info)
            self.assertIn("project_name", venv_info)
            self.assertIn("age_days", venv_info)
            self.assertIn("size_mb", venv_info)
            self.assertIn("meets_criteria", venv_info)
    
    def test_scan_for_venvs_invalid_directory(self):
        """Test scanning with invalid directory."""
        with self.assertRaises(ValueError):
            scan_for_venvs("/nonexistent/directory")
    
    def test_filter_venvs_by_criteria(self):
        """Test filtering venvs by criteria."""
        venv_list = [
            {"age_days": 100, "size_mb": 300},
            {"age_days": 30, "size_mb": 300},
            {"age_days": 100, "size_mb": 50},
        ]
        
        filtered = filter_venvs_by_criteria(venv_list, days_unused=60, min_size_mb=200)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["age_days"], 100)
        self.assertEqual(filtered[0]["size_mb"], 300)


if __name__ == "__main__":
    unittest.main()
