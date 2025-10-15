# Virtual Environment Remover

A GUI application for managing and removing unused Python virtual environments. This tool helps free up disk space by identifying and selectively deleting old or large venv folders across your project directories.

## Features

- **GUI Interface**: User-friendly graphical interface built with tkinter
- **Configurable Parameters**: Customize scan criteria (root directory, age, size)
- **Selective Deletion**: Choose which venvs to delete with checkbox selection
- **Project Information**: View project folder names and venv details
- **Dry Run Mode**: Preview deletions before committing
- **Space Calculation**: See how much disk space will be freed
- **Multi-threaded Scanning**: Non-blocking UI during directory scans
- **Requirements.txt Generation**: Automatically create requirements.txt before deletion for easy reinstallation

## Installation

### Option 1: Use Pre-built Executable (Recommended for Windows)

1. Download `VenvRemover.exe` from the releases
2. Double-click to run - no Python installation required!

### Option 2: Run from Source

**Prerequisites:**
- Python 3.7 or higher
- tkinter (usually comes with Python)

**Setup:**
1. Clone or download this repository
2. No additional dependencies required (uses only Python standard library)

```bash
cd "Venv remover"
python venv_remover_gui.py
```

### Option 3: Build Your Own Executable

**Prerequisites:**
- Python 3.7 or higher
- PyInstaller (will be installed automatically if not present)

**Build Steps:**
```bash
cd "Venv remover"
python build_exe.py
```

The executable will be created in the `dist/` folder as `VenvRemover.exe`.

**Build Options:**
- Single-file executable: ✓ (included)
- No console window: ✓ (included)
- Optimized size: ✓ (~10.6 MB)
- Strip debug symbols: ✓ (attempted)
- UPX compression: ✓ (if available)

## Usage

### Running the GUI Application

```bash
python venv_remover_gui.py
```

### Configuration Panel

1. **Root Directory**: The base directory to scan for venv folders
   - Use the "Browse" button to select a directory
   - Default: `D:/`

2. **Days Unused**: Minimum age (in days) for venvs to be considered for deletion
   - Default: 60 days
   - Range: 1-365 days

3. **Min Size (MB)**: Minimum size (in MB) for venvs to be considered for deletion
   - Default: 200 MB
   - Range: 1-10000 MB

4. **Dry Run**: Preview mode toggle
   - Checked: Preview only (no actual deletion)
   - Unchecked: Actual deletion mode
   - Default: Checked (enabled)

5. **Create requirements.txt before deletion**: Option to preserve dependencies
   - Checked: Generate requirements.txt in project folder before deleting venv
   - Unchecked: Skip requirements generation
   - Default: Checked (enabled)

### Scanning for Virtual Environments

1. Configure your scan parameters in the Configuration panel
2. Click "Scan for Venvs" button
3. Wait for the scan to complete (status shown in status bar)
4. Review the list of found virtual environments

### Selecting and Deleting Venvs

1. Click on items in the list to toggle selection (checkbox appears)
2. Use "Select All" or "Deselect All" for bulk selection
3. Review the "Space" indicator to see how much space will be freed
4. Optionally enable/disable "Create requirements.txt before deletion"
5. Click "Delete Selected" to proceed
6. Confirm the deletion in the popup dialog
7. If requirements generation is enabled, a requirements.txt file will be created in each project folder before deletion

### Reinstalling Dependencies

After deleting a venv, you can recreate it and reinstall dependencies:

```bash
# Navigate to your project folder
cd path/to/your/project

# Create new venv
python -m venv venv

# Activate venv (Windows)
venv\Scripts\activate

# Activate venv (Unix/Linux)
source venv/bin/activate

# Install dependencies from requirements.txt
pip install -r requirements.txt
```

### Understanding the Display

The treeview displays the following columns:

- **Select**: Checkbox for selection
- **Project Name**: Name of the parent project folder
- **Venv Path**: Full path to the venv folder
- **Age (Days)**: Days since last modification
- **Size (MB)**: Total size of the venv folder
- **Meets Criteria**: Whether the venv meets age and size criteria

## Project Structure

```
Venv remover/
├── venv_remover_gui.py       # Main GUI application
├── Venv_Remover.py            # Original CLI version
├── build_exe.py               # Executable builder script
├── README.md                  # This file
├── utils/                     # Utility modules
│   ├── __init__.py
│   ├── venv_scanner.py        # Scanning and detection logic
│   ├── venv_deleter.py        # Deletion logic
│   └── requirements_generator.py  # Requirements.txt generation
├── Test_py/                   # Unit tests
│   ├── __init__.py
│   ├── test_venv_scanner.py   # Tests for scanner module
│   ├── test_venv_deleter.py   # Tests for deleter module
│   └── test_requirements_generator.py  # Tests for requirements generator
├── dist/                      # Build output (created after building)
│   └── VenvRemover.exe        # Standalone executable
└── .clinerules/               # Development rules and context
    ├── .clinerules.md
    ├── .Common_venv.md
    └── prompt_context_log.md
```

## Module Documentation

### utils/venv_scanner.py

Contains functions for scanning and detecting virtual environments:

- `get_folder_size(folder_path)`: Calculate folder size in MB
- `get_venv_age_days(venv_path)`: Calculate venv age in days
- `scan_for_venvs(root_dir, days_unused, min_size_mb)`: Scan directory tree for venvs
- `filter_venvs_by_criteria(venv_list, days_unused, min_size_mb)`: Filter venvs by criteria

### utils/venv_deleter.py

Contains functions for deleting virtual environments:

- `delete_venv(venv_path, dry_run)`: Delete a single venv
- `delete_multiple_venvs(venv_paths, dry_run)`: Delete multiple venvs
- `calculate_space_freed(venv_list)`: Calculate total space to be freed

### utils/requirements_generator.py

Contains functions for generating requirements.txt from virtual environments:

- `get_venv_python_path(venv_path)`: Get Python executable path in venv
- `generate_requirements_from_venv(venv_path, output_path, overwrite)`: Generate requirements.txt from a single venv
- `generate_requirements_for_multiple_venvs(venv_info_list, overwrite)`: Generate requirements.txt for multiple venvs

## Running Tests

The project includes comprehensive unit tests for all utility functions.

### Run all tests:

```bash
python -m unittest discover Test_py -v
```

### Run specific test modules:

```bash
# Test venv scanner
python -m unittest Test_py.test_venv_scanner -v

# Test venv deleter
python -m unittest Test_py.test_venv_deleter -v

# Test requirements generator
python -m unittest Test_py.test_requirements_generator -v
```

All tests should pass before using the application.

**Test Summary:**
- test_venv_scanner: 5 tests
- test_venv_deleter: 8 tests
- test_requirements_generator: 7 tests
- **Total: 20 tests**

## Safety Features

1. **Dry Run Mode**: Default mode prevents accidental deletion
2. **Confirmation Dialog**: Always asks for confirmation before deletion
3. **Size and Age Criteria**: Only targets venvs meeting specific criteria
4. **Error Handling**: Gracefully handles permission errors and missing files
5. **Selective Deletion**: User chooses exactly which venvs to delete
6. **Requirements Preservation**: Automatically backs up dependency information before deletion

## Original CLI Version

The original command-line version is still available in `Venv_Remover.py`. To use it:

1. Edit the configuration variables at the top of the file:
   - `ROOT_DIR`: Directory to scan
   - `DAYS_UNUSED`: Age threshold
   - `MIN_SIZE_MB`: Size threshold
   - `DRY_RUN`: Preview mode toggle

2. Run the script:
   ```bash
   python Venv_Remover.py
   ```

## Troubleshooting

### Issue: Scan is slow

- Large directory trees take time to scan
- Consider narrowing the root directory to specific project folders
- The GUI remains responsive during scanning (multi-threaded)

### Issue: Permission errors during deletion

- Some venv files may be locked by running processes
- Close any IDEs or terminals using the venv
- Run with administrator privileges if necessary

### Issue: Venvs not appearing in scan

- Check that the folder is named exactly "venv"
- Verify the venv meets age and size criteria
- Reduce the criteria thresholds to see more results

### Issue: Requirements.txt generation fails

- Ensure the venv has a valid Python executable
- Check that pip is installed in the venv
- Verify you have write permissions to the project folder
- Some venvs may have corrupted pip installations

## Contributing

Follow the coding standards defined in `.clinerules/.clinerules.md`:

- Use snake_case for variables, functions, and modules
- Use PascalCase for classes
- Include docstrings for all functions
- Write unit tests before implementing features
- Keep functions under 150 lines
- Keep files under 600 lines

## License

This project is provided as-is for personal use.

## Author

Created for efficient virtual environment management and disk space optimization.
