def move_declarations_to_top(fortran_code: str) -> str:
    """
    Rearranges Fortran code so that any lines that contain declarations
    (indicated by the occurrence of "::") are moved to the beginning,
    just after the header (e.g. after the "implicit none" or the "program"/"module"
    statement), i.e. before the executable statements.
    
    Parameters:
        fortran_code (str): The original Fortran source code as a multiline string.
    
    Returns:
        str: The modified Fortran code with declaration lines moved.
    """
    # Split code into individual lines.
    lines = fortran_code.splitlines()
    
    # Separate out declaration lines (ignoring lines that are full-line comments)
    declaration_lines = []
    other_lines = []
    for line in lines:
        stripped = line.strip()
        # Check if line has declaration operator and is not just a comment.
        if "::" in line and not stripped.startswith("!"):
            declaration_lines.append(line)
        else:
            other_lines.append(line)
    
    # Determine the insertion point.
    # Prefer inserting declarations after the header section.
    # Look for a line with "implicit none" (case insensitive).
    insertion_index = 0
    for idx, line in enumerate(other_lines):
        if "implicit none" in line.lower():
            # Found header line, now look for the next blank line in order to keep any header spacing.
            insertion_index = idx + 1
            for j in range(idx + 1, len(other_lines)):
                if other_lines[j].strip() == "":
                    insertion_index = j + 1
                    break
            break
    # If no "implicit none" is found, check if the very first line starts with "program" or "module"
    if insertion_index == 0 and other_lines:
        first = other_lines[0].lstrip().lower()
        if first.startswith("program") or first.startswith("module"):
            insertion_index = 1
        else:
            insertion_index = 0  # Otherwise, insert at the very beginning.
    
    # Insert the declarations into the other_lines at the computed index.
    new_lines = other_lines[:insertion_index] + declaration_lines + other_lines[insertion_index:]
    
    # Reassemble the code as a single string.
    return "\n".join(new_lines)

if __name__ == "__main__":
    from sys import argv
    src_file = argv[1]
    fortran_code = open(src_file, "r").read()
    new_code = move_declarations_to_top(fortran_code)
    print(new_code)
