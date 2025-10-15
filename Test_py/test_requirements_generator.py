"""
Unit tests for requirements_generator utility module.
"""
import unittest
import os
import tempfile
import shutil
from utils.requirements_generator import (
    get_venv_python_path,
    generate_requirements_from_venv,
    generate_requirements_for_multiple_venvs
)


class TestRequirementsGenerator(unittest.TestCase):
    """Test cases for requirements generator functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_project_dir = os.path.join(self.test_dir, "test_project")
        self.test_venv_dir = os.path.join(self.test_project_dir, "venv")
        os.makedirs(self.test_venv_dir, exist_ok=True)
        
        # Create mock venv structure (Windows)
        scripts_dir = os.path.join(self.test_venv_dir, "Scripts")
        os.makedirs(scripts_dir, exist_ok=True)
        
        # Create a mock python.exe
        self.python_exe_path = os.path.join(scripts_dir, "python.exe")
        with open(self.python_exe_path, "w") as f:
            f.write("mock python")
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_get_venv_python_path_windows(self):
        """Test getting Python path in Windows venv."""
        python_path = get_venv_python_path(self.test_venv_dir)
        self.assertIsNotNone(python_path)
        if python_path:
            self.assertTrue(python_path.endswith("python.exe"))
    
    def test_get_venv_python_path_nonexistent(self):
        """Test getting Python path from nonexistent venv."""
        empty_venv = os.path.join(self.test_dir, "empty_venv")
        os.makedirs(empty_venv, exist_ok=True)
        python_path = get_venv_python_path(empty_venv)
        self.assertIsNone(python_path)
    
    def test_generate_requirements_from_venv_empty_path(self):
        """Test generation with empty venv path."""
        with self.assertRaises(ValueError):
            generate_requirements_from_venv("", "output.txt")
    
    def test_generate_requirements_from_venv_empty_output(self):
        """Test generation with empty output path."""
        with self.assertRaises(ValueError):
            generate_requirements_from_venv(self.test_venv_dir, "")
    
    def test_generate_requirements_from_venv_nonexistent_path(self):
        """Test generation with nonexistent venv path."""
        fake_path = os.path.join(self.test_dir, "fake_venv")
        output_path = os.path.join(self.test_project_dir, "requirements.txt")
        success, message = generate_requirements_from_venv(fake_path, output_path)
        self.assertFalse(success)
        self.assertIn("does not exist", message)
    
    def test_generate_requirements_for_multiple_venvs_empty_list(self):
        """Test generation for empty venv list."""
        result = generate_requirements_for_multiple_venvs([])
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["successful"], 0)
        self.assertEqual(result["failed"], 0)
    
    def test_generate_requirements_for_multiple_venvs_missing_info(self):
        """Test generation with missing venv info."""
        venv_list = [
            {"venv_path": self.test_venv_dir},  # Missing project_path
        ]
        result = generate_requirements_for_multiple_venvs(venv_list)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["successful"], 0)
        self.assertEqual(result["failed"], 1)


if __name__ == "__main__":
    unittest.main()
