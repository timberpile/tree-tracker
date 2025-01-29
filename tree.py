import os
import json
import zipfile
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Tree:
    name: str
    parent: Optional['Tree']
    is_dir: bool
    size: int
    mdate: float
    children: List['Tree'] = field(default_factory=list)

    @property
    def size_pretty(self) -> str:
        """
        Returns the size of the file/directory in a human-readable format (B, kB, MB, GB, etc.).
        """
        suffixes = ['B', 'kB', 'MB', 'GB', 'TB', 'PB']
        size = self.size
        i = 0
        while size >= 1024 and i < len(suffixes)-1:
            size /= 1024.
            i += 1
        return f"{size:.0f} {suffixes[i]}"

    def to_str(self, level=0) -> str:
        line = "  " * level + self.name
        if not self.is_dir:
            line += f" [{self.size_pretty}]"

        lines = []
        lines.append(line)
        for child in self.children:
            lines.append(child.to_str(level + 1))

        return "\n".join(lines)

    def to_json(self):
        def tree_to_dict(tree):
            d = {
                "name": tree.name,
                "mdate": tree.mdate,
            }

            if tree.is_dir:
                d["is_dir"] = True
                d["children"] = [tree_to_dict(child) for child in tree.children]
            else:
                d["size"] = tree.size

            return d

        return json.dumps(tree_to_dict(self), indent=4)

    @staticmethod
    def from_json(json_str: str):
        def dict_to_tree(d: Dict[str, Any], parent=None):
            is_dir = d.get("is_dir", False)
            tree = Tree(
                name=d["name"],
                parent=parent,
                is_dir=is_dir,
                mdate=d["mdate"],
                size=0 if is_dir else d["size"],
                children=[]
            )

            for child_dict in d.get("children", []):
                tree.children.append(dict_to_tree(child_dict, tree))

            return tree

        return dict_to_tree(json.loads(json_str))

    @classmethod
    def from_file(cls, path: str):
        if not os.path.exists(path):
            raise ValueError(f"File '{path}' doesn't exist")
        ext = os.path.splitext(path)[1]
        if ext == ".json":
            with open(path, "r") as f:
                return cls.from_json(f.read())
        elif ext == ".zip":
            with zipfile.ZipFile(path, "r") as zipf:
                files = zipf.namelist()
                if len(files) != 1:
                    raise ValueError("Zip file must contain exactly one file!")
                with zipf.open(files[0]) as f:
                    return cls.from_json(f.read().decode())
        else:
            raise ValueError(f"Input file has invalid extension '{ext}'. Only .json and .zip are allowed.")