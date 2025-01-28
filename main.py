import os
import argparse
import zipfile
from tree import Tree
from tree_scanner import TreeScanner
from tree_creator import TreeCreator

def main():
    parser = argparse.ArgumentParser(description="Process a directory and generate a TreeTracker object, or create a file structure from an existing config file.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan a directory and create an output file.")
    scan_parser.add_argument("directory_path", type=str, help="The path to the directory to process.")
    scan_parser.add_argument("--print", action="store_true", help="Print the file tree in the terminal.")
    scan_parser.add_argument("--ignore-errors", action="store_true", help="When files or directories can't be read, simply ignore them.")
    scan_parser.add_argument('--ignore-file', type=str, default=None, help='File with ignore patterns.')
    scan_parser.add_argument("--output-file", type=str, default=None, help="JSON file to store results in.")
    scan_parser.add_argument("--output-file-compressed", type=str, default=None, help="JSON file to store resultsin.")

    create_parser = subparsers.add_parser("create", help="Create a tree structure from a generated output file.")
    create_parser.add_argument("destination_path", type=str, help="The path to create the tree in.")
    create_parser.add_argument("input_file", type=str, help="The path to the input file (either .json or .zip).")

    args = parser.parse_args()

    if args.command == 'scan':
        scanner = TreeScanner()
        scanner.ignore_errors = args.ignore_errors

        if args.ignore_file:
            with open(args.ignore_file, "r") as f:
                scanner.exclude_patterns = [x for x in f.readlines() if x]

        print(f"Generating tree...")
        tree = scanner.scan_tree(args.directory_path)
        if tree:
            print(f"Tree generation finished!")
        else:
            print(f"Failed to generate tree")
            return

        if args.print:
            print(tree.to_str())

        if args.output_file:
            print(f"Writing Tree to JSON '{args.output_file}'...")
            with open(args.output_file, "w") as f:
                f.write(tree.to_json())
            print(f"Wrote Tree to JSON '{args.output_file}'")

        if args.output_file_compressed:
            print(f"Writing Tree to ZIP '{args.output_file_compressed}'...")
            with zipfile.ZipFile(args.output_file_compressed, "w", zipfile.ZIP_DEFLATED) as f:
                f.writestr("tree.json", tree.to_json().encode())
            print(f"Wrote Tree to ZIP '{args.output_file_compressed}'")
    elif args.command == 'create':
        if not os.path.exists(args.input_file):
            print(f"Input file '{args.input_file}' doesn't exist")
            exit(1)

        print("Importing tree...")
        tree = Tree.from_file(args.input_file)
        print("Tree imported")

        print("Creating tree...")
        TreeCreator().create_tree(args.destination_path, tree)
        print("Tree created successfully")

if __name__ == "__main__":
    main()
