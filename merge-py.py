import os

def collect_py_files(directory: str) -> list:
    """
    Recursively collects all Python (.py) file paths from the specified directory.
    """
    py_file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                py_file_paths.append(os.path.join(root, file))
    return py_file_paths


def add_file_header_and_footer(file_path: str) -> str:
    """
    Reads the content of a file, adds a comment at the top with the file path and name,
    and appends a comment at the end to mark the file boundary.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.readlines()

    # Check if the first line is already a comment with the file path
    if content and content[0].startswith("# File:"):
        header = "".join(content)
    else:
        # Add header with file path and name
        header = f"# File: {file_path}\n\n" + "".join(content)

    # Add footer
    footer = f"\n\n# --- End of {os.path.basename(file_path)} ---\n"
    return header + footer


def merge_and_output(directory: str, output_directory: str):
    """
    Merges all Python files in the directory into a single output file with headers and footers.
    Ensures unique numbering for output files.
    """
    # Collect all Python files
    files = collect_py_files(directory)

    # Prepare merged content with headers and footers
    merged_content = []
    for file_path in files:
        try:
            file_content_with_header_footer = add_file_header_and_footer(file_path)
            merged_content.append(file_content_with_header_footer)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Generate unique output file name
    base_output_name = "collection-py"
    numbering = 1
    while True:
        output_file = os.path.join(output_directory, f"{base_output_name}-{numbering}.py")
        if not os.path.exists(output_file):
            break
        numbering += 1

    # Write merged content to output file
    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write("\n\n# --- Start of Merged File ---\n\n")
        outfile.write("\n\n".join(merged_content))
        outfile.write("\n\n# --- End of Merged File ---\n")

    print(f"Merged file created: {output_file}")


# Example usage
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    source_directory = os.path.join(current_dir, "src/app/adapters")
    output_directory = os.path.join(current_dir, "output")

    os.makedirs(output_directory, exist_ok=True)  # Ensure output directory exists
    merge_and_output(source_directory, output_directory)