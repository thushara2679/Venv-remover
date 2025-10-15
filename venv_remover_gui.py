"""
Main GUI application for Virtual Environment Remover.
Provides a graphical interface for scanning and removing unused venv folders.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
from typing import List, Dict
from utils.venv_scanner import scan_for_venvs
from utils.venv_deleter import delete_multiple_venvs, calculate_space_freed
from utils.requirements_generator import generate_requirements_for_multiple_venvs


class VenvRemoverGUI:
    """
    Main GUI class for the Virtual Environment Remover application.
    
    Provides interface for configuring scan parameters, displaying found venvs,
    and selectively deleting virtual environments.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI application.
        
        Args:
            root (tk.Tk): The root tkinter window.
        """
        self.root = root
        self.root.title("Virtual Environment Remover")
        self.root.geometry("1000x700")
        
        # Configuration variables
        self.root_dir_var = tk.StringVar(value="D:/")
        self.days_unused_var = tk.IntVar(value=60)
        self.min_size_mb_var = tk.IntVar(value=200)
        self.dry_run_var = tk.BooleanVar(value=True)
        self.create_requirements_var = tk.BooleanVar(value=True)
        
        # Data storage
        self.venv_list: List[Dict] = []
        self.selected_indices: List[int] = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface components."""
        self._create_config_frame()
        self._create_action_frame()
        self._create_treeview_frame()
        self._create_status_frame()
    
    def _create_config_frame(self):
        """Create the configuration panel frame."""
        config_frame = ttk.LabelFrame(self.root, text="Configuration", padding="10")
        config_frame.pack(fill="x", padx=10, pady=5)
        
        # Root Directory
        ttk.Label(config_frame, text="Root Directory:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        dir_entry = ttk.Entry(config_frame, textvariable=self.root_dir_var, width=50)
        dir_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(config_frame, text="Browse", command=self._browse_directory).grid(row=0, column=2, padx=5, pady=5)
        
        # Days Unused
        ttk.Label(config_frame, text="Days Unused:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Spinbox(config_frame, from_=1, to=365, textvariable=self.days_unused_var, width=20).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Minimum Size
        ttk.Label(config_frame, text="Min Size (MB):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Spinbox(config_frame, from_=1, to=10000, textvariable=self.min_size_mb_var, width=20).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Dry Run
        ttk.Checkbutton(config_frame, text="Dry Run (Preview Only)", variable=self.dry_run_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Create Requirements
        ttk.Checkbutton(config_frame, text="Create requirements.txt before deletion", variable=self.create_requirements_var).grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    
    def _create_action_frame(self):
        """Create the action buttons frame."""
        action_frame = ttk.Frame(self.root, padding="10")
        action_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(action_frame, text="Scan for Venvs", command=self._scan_venvs).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Select All", command=self._select_all).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Deselect All", command=self._deselect_all).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Delete Selected", command=self._delete_selected).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Refresh", command=self._refresh_display).pack(side="left", padx=5)
    
    def _create_treeview_frame(self):
        """Create the treeview frame for displaying venvs."""
        tree_frame = ttk.LabelFrame(self.root, text="Found Virtual Environments", padding="10")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create treeview with scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        tree_scroll_y.pack(side="right", fill="y")
        
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Project", "Path", "Age", "Size", "Status"),
            show="tree headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode="extended"
        )
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Configure columns
        self.tree.heading("#0", text="Select")
        self.tree.heading("Project", text="Project Name")
        self.tree.heading("Path", text="Venv Path")
        self.tree.heading("Age", text="Age (Days)")
        self.tree.heading("Size", text="Size (MB)")
        self.tree.heading("Status", text="Meets Criteria")
        
        self.tree.column("#0", width=50, stretch=False)
        self.tree.column("Project", width=150)
        self.tree.column("Path", width=400)
        self.tree.column("Age", width=100)
        self.tree.column("Size", width=100)
        self.tree.column("Status", width=100)
        
        self.tree.pack(fill="both", expand=True)
        
        # Add checkboxes via tags
        self.tree.tag_configure("unchecked", image="")
        self.tree.tag_configure("checked", image="")
        
        # Bind click event
        self.tree.bind("<Button-1>", self._on_tree_click)
    
    def _create_status_frame(self):
        """Create the status bar frame."""
        status_frame = ttk.Frame(self.root, padding="5")
        status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready", relief="sunken")
        self.status_label.pack(side="left", fill="x", expand=True)
        
        self.space_label = ttk.Label(status_frame, text="Space: 0 MB", relief="sunken")
        self.space_label.pack(side="right", padx=5)
    
    def _browse_directory(self):
        """Open directory browser dialog."""
        directory = filedialog.askdirectory(initialdir=self.root_dir_var.get())
        if directory:
            self.root_dir_var.set(directory)
    
    def _scan_venvs(self):
        """Scan for virtual environments in a separate thread."""
        self.status_label.config(text="Scanning...")
        self.root.update()
        
        # Run scan in separate thread to prevent GUI freeze
        thread = threading.Thread(target=self._perform_scan)
        thread.daemon = True
        thread.start()
    
    def _perform_scan(self):
        """Perform the actual scanning operation."""
        try:
            root_dir = self.root_dir_var.get()
            days_unused = self.days_unused_var.get()
            min_size_mb = self.min_size_mb_var.get()
            
            self.venv_list = scan_for_venvs(root_dir, days_unused, min_size_mb)
            
            # Update GUI in main thread
            self.root.after(0, self._update_treeview)
            self.root.after(0, lambda: self.status_label.config(text=f"Scan complete. Found {len(self.venv_list)} venvs."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Scan Error", f"Error during scan: {str(e)}"))
            self.root.after(0, lambda: self.status_label.config(text="Scan failed"))
    
    def _update_treeview(self):
        """Update the treeview with scanned venv data."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.selected_indices = []
        
        # Populate treeview
        for idx, venv_info in enumerate(self.venv_list):
            project_name = venv_info["project_name"]
            venv_path = venv_info["venv_path"]
            age_days = f"{int(venv_info['age_days'])}"
            size_mb = f"{int(venv_info['size_mb'])}"
            meets_criteria = "Yes" if venv_info["meets_criteria"] else "No"
            
            self.tree.insert(
                "",
                "end",
                iid=str(idx),
                text="☐",
                values=(project_name, venv_path, age_days, size_mb, meets_criteria),
                tags=("unchecked",)
            )
        
        self._update_space_label()
    
    def _on_tree_click(self, event):
        """Handle tree item click for checkbox toggle."""
        region = self.tree.identify("region", event.x, event.y)
        if region == "tree":
            item = self.tree.identify_row(event.y)
            if item:
                self._toggle_selection(item)
    
    def _toggle_selection(self, item: str):
        """Toggle the selection state of a tree item."""
        idx = int(item)
        
        if idx in self.selected_indices:
            self.selected_indices.remove(idx)
            self.tree.item(item, text="☐", tags=("unchecked",))
        else:
            self.selected_indices.append(idx)
            self.tree.item(item, text="☑", tags=("checked",))
        
        self._update_space_label()
    
    def _select_all(self):
        """Select all items in the treeview."""
        self.selected_indices = list(range(len(self.venv_list)))
        for idx in self.selected_indices:
            self.tree.item(str(idx), text="☑", tags=("checked",))
        self._update_space_label()
    
    def _deselect_all(self):
        """Deselect all items in the treeview."""
        for idx in self.selected_indices:
            self.tree.item(str(idx), text="☐", tags=("unchecked",))
        self.selected_indices = []
        self._update_space_label()
    
    def _update_space_label(self):
        """Update the space label with selected venv sizes."""
        if not self.selected_indices:
            self.space_label.config(text="Space: 0 MB")
            return
        
        selected_venvs = [self.venv_list[i] for i in self.selected_indices]
        total_space = calculate_space_freed(selected_venvs)
        self.space_label.config(text=f"Space: {int(total_space)} MB")
    
    def _delete_selected(self):
        """Delete the selected virtual environments."""
        if not self.selected_indices:
            messagebox.showwarning("No Selection", "Please select venvs to delete.")
            return
        
        selected_venvs = [self.venv_list[i] for i in self.selected_indices]
        total_space = calculate_space_freed(selected_venvs)
        
        dry_run = self.dry_run_var.get()
        create_requirements = self.create_requirements_var.get()
        mode_text = "PREVIEW" if dry_run else "DELETE"
        
        message = (
            f"You are about to {mode_text.lower()} {len(selected_venvs)} venv(s).\n"
            f"Total space: {int(total_space)} MB\n"
        )
        
        if create_requirements:
            message += "\nrequirements.txt will be created for each venv.\n"
        
        message += "\nContinue?"
        
        confirm = messagebox.askyesno(f"Confirm {mode_text}", message)
        
        if not confirm:
            return
        
        # Perform deletion
        self._perform_deletion(selected_venvs, dry_run, create_requirements)
    
    def _perform_deletion(self, selected_venvs: List[Dict], dry_run: bool, create_requirements: bool):
        """Perform the deletion operation with optional requirements generation."""
        self.status_label.config(text="Processing deletions...")
        self.root.update()
        
        requirements_result = None
        
        # Generate requirements.txt if requested
        if create_requirements:
            self.status_label.config(text="Generating requirements.txt files...")
            self.root.update()
            requirements_result = generate_requirements_for_multiple_venvs(selected_venvs, overwrite=True)
        
        # Perform deletion
        self.status_label.config(text="Deleting venvs...")
        self.root.update()
        venv_paths = [venv["venv_path"] for venv in selected_venvs]
        deletion_result = delete_multiple_venvs(venv_paths, dry_run)
        
        # Build results message
        message = "=== Deletion Results ===\n"
        message += f"Total: {deletion_result['total']}\n"
        message += f"Successful: {deletion_result['successful']}\n"
        message += f"Failed: {deletion_result['failed']}\n"
        
        if requirements_result:
            message += "\n=== Requirements Generation ===\n"
            message += f"Total: {requirements_result['total']}\n"
            message += f"Successful: {requirements_result['successful']}\n"
            message += f"Failed: {requirements_result['failed']}\n"
        
        if deletion_result['failed'] > 0:
            failed_details = "\n".join([
                msg for path, success, msg in deletion_result['results'] if not success
            ])
            message += f"\nFailed deletions:\n{failed_details[:500]}"
        
        messagebox.showinfo("Operation Results", message)
        self.status_label.config(text="Operation complete")
        
        # Refresh the display
        if not dry_run:
            self._scan_venvs()
    
    def _refresh_display(self):
        """Refresh the venv display."""
        self._update_treeview()
        self.status_label.config(text="Display refreshed")


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = VenvRemoverGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
