import os
from dataclasses import dataclass
from tree import Tree
from pathlib import Path

@dataclass
class TreeCreator:
    def create_tree(self, base_dir_: str, tree: Tree):
        def create(base_dir: str, tree: Tree):
            tree_path = os.path.join(base_dir, tree.name)
            if tree.is_dir:
                os.makedirs(tree_path, exist_ok=True)
                os.utime(tree_path, (tree.mdate, tree.mdate))
                for child in tree.children:
                    create(tree_path, child)
            else:
                if os.path.exists(tree_path):
                    return
                Path(tree_path).touch()
                os.utime(tree_path, (tree.mdate, tree.mdate))

        os.makedirs(base_dir_, exist_ok=True)
        create(base_dir_, tree)
