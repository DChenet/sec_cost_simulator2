import os
from pathlib import Path


class ExportManager:
    def __init__(self):
        self.project_root = os.getcwd()

    def create_export_dir(self, root: Path = None):
        if not root:
            Path(self.project_root).mkdir(parents=True, exist_ok=True)

    def get_export_dir(self):
        return Path(self.project_root)