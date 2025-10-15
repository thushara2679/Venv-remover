"""
Unit tests for venv_deleter utility module.
"""
import unittest
import os
import tempfile
import shutil
from utils.venv_deleter import (
    delete_venv,
    delete_multiple_venvs,
    calculate_space_freed
)


class TestVenvDeleter(unittest.TestCase):
    """Test cases for venv deleter functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_venv_dir = os.path.join(self.test_dir, "test_venv")
        os.makedirs(self.test_venv_dir, exist_ok=True)
        
        # Create test file
        test_file = os.path.join(self.test_venv_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Test content")
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_delete_venv_dry_run(self):
        """Test venv deletion in dry run mode."""
        success, message = delete_venv(self.test_venv_dir, dry_run=True)
        self.assertTrue(success)
        self.assertIn("DRY RUN", message)
        self.assertTrue(os.path.exists(self.test_venv_dir))
    
    def test_delete_venv_actual(self):
        """Test actual venv deletion."""
        success, message = delete_venv(self.test_venv_dir, dry_run=False)
        self.assertTrue(success)
        self.assertIn("Successfully deleted", message)
        self.assertFalse(os.path.exists(self.test_venv_dir))
    
    def test_delete_venv_nonexistent(self):
        """Test deletion of nonexistent path."""
        fake_path = os.path.join(self.test_dir, "nonexistent")
        success, message = delete_venv(fake_path, dry_run=False)
        self.assertFalse(success)
        self.assertIn("does not exist", message)
    
    def test_delete_venv_empty_path(self):
        """Test deletion with empty path."""
        with self.assertRaises(ValueError):
            delete_venv("", dry_run=False)
    
    def test_delete_multiple_venvs_dry_run(self):
        """Test multiple venv deletion in dry run mode."""
        venv1 = os.path.join(self.test_dir, "venv1")
        venv2 = os.path.join(self.test_dir, "venv2")
        os.makedirs(venv1, exist_ok=True)
        os.makedirs(venv2, exist_ok=True)
        
        result = delete_multiple_venvs([venv1, venv2], dry_run=True)
        
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["successful"], 2)
        self.assertEqual(result["failed"], 0)
        self.assertTrue(os.path.exists(venv1))
        self.assertTrue(os.path.exists(venv2))
    
    def test_delete_multiple_venvs_actual(self):
        """Test actual multiple venv deletion."""
        venv1 = os.path.join(self.test_dir, "venv1")
        venv2 = os.path.join(self.test_dir, "venv2")
        os.makedirs(venv1, exist_ok=True)
        os.makedirs(venv2, exist_ok=True)
        
        result = delete_multiple_venvs([venv1, venv2], dry_run=False)
        
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["successful"], 2)
        self.assertEqual(result["failed"], 0)
        self.assertFalse(os.path.exists(venv1))
        self.assertFalse(os.path.exists(venv2))
    
    def test_calculate_space_freed(self):
        """Test space calculation."""
        venv_list = [
            {"size_mb": 100.5},
            {"size_mb": 200.3},
            {"size_mb": 50.2},
        ]
        
        total = calculate_space_freed(venv_list)
        self.assertAlmostEqual(total, 351.0, places=1)
    
    def test_calculate_space_freed_empty(self):
        """Test space calculation with empty list."""
        total = calculate_space_freed([])
        self.assertEqual(total, 0.0)


if __name__ == "__main__":
    unittest.main()
