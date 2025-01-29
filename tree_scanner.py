import os
import pathspec
from dataclasses import dataclass, field
from typing import Optional, List
from tree import Tree

@dataclass
class TreeScanner:
    exclude_patterns: List[str] = field(default_factory=list)
    ignore_errors: bool = False

    def exclude_path(self, path:str):
        if ".chunks" in path:
            pass
        spec = pathspec.PathSpec.from_lines("gitwildmatch", self.exclude_patterns)
        match = spec.match_file(path.replace("\\", "/"))
        return match

    def scan_tree(self, path: str) -> Optional['Tree']:
        global entry_count
        entry_count = 0

        def scan_dir(dir_path: str, parent: Optional['Tree'] = None) -> Optional['Tree']:
            global entry_count

            try:
                entries = os.listdir(dir_path)
            except PermissionError as ex:
                if self.ignore_errors:
                    return None
                else:
                    raise ex

            dir_metadata = os.stat(dir_path)

            dir_tracker = Tree(
                name=os.path.basename(dir_path),
                parent=parent,
                is_dir=True,
                size=0,
                mdate=int(dir_metadata.st_mtime)
            )

            for entry in entries:
                child_path = os.path.join(dir_path, entry)
                if self.exclude_path(child_path):
                    continue

                entry_count += 1
                if entry_count % 1000 == 0:
                    print(f"Scanning entry nr. {entry_count} ({child_path})...")

                if os.path.isdir(child_path):
                    child = scan_dir(child_path, dir_tracker)
                    if child:
                        dir_tracker.children.append(child)
                else:
                    try:
                        metadata = os.stat(child_path)
                        child = Tree(
                            name=entry,
                            parent=dir_tracker,
                            is_dir=False,
                            size=metadata.st_size,
                            mdate=metadata.st_mtime
                        )
                        dir_tracker.children.append(child)
                    except (PermissionError, FileNotFoundError) as ex:
                        if self.ignore_errors:
                            continue
                        else:
                            raise ex

            return dir_tracker

        return scan_dir(os.path.abspath(path))
