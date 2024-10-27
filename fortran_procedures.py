import re

def extract_procedures(lines):
    """
    Extracts subroutine and function definitions from a list of lines of Fortran code.

    This function identifies and captures Fortran subroutine and function definitions,
    including multi-line definitions with various type and attribute specifiers, such as
    "pure", "elemental", "impure", and Fortran types (e.g., real, integer, logical). It
    collects each procedure's lines until it encounters an "end" statement and stores
    them in a dictionary.

    Args:
        lines (list of str): A list of lines from a Fortran source file.

    Returns:
        dict: A dictionary where keys are tuples of the form ("subroutine", "name") or
              ("function", "name"), with "name" being the lowercase procedure name. 
              Values are lists of strings containing the lines of the procedure.
    """
    procedure_dict = {}
    current_proc_type = None
    current_proc_name = None
    current_proc_lines = []
    # Define regex pattern for procedure definitions
    proc_def_pattern = re.compile(
        r'^\s*(?!end\b)(?:[\w\s\(\),=\*\:\']+)?\b(function|subroutine)\b\s+(\w+)',
        re.IGNORECASE
    )
    # Define regex pattern for end of procedure
    proc_end_pattern = re.compile(
        r'^\s*end\b(?:\s+(function|subroutine))?(?:\s+(\w+))?',
        re.IGNORECASE
    )
    i = 0
    while i < len(lines):
        line = lines[i]
        line_stripped = line.strip()
        if current_proc_type is None:
            # Look for procedure definition
            match = proc_def_pattern.match(line_stripped)
            if match:
                # We have found a procedure definition
                proc_type = match.group(1).lower()
                proc_name = match.group(2).lower()
                current_proc_type = proc_type
                current_proc_name = proc_name
                current_proc_lines = [line]
            else:
                # Handle multi-line procedure definitions
                proc_def_lines = [line]
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    proc_def_lines.append(next_line)
                    combined_lines = ' '.join(proc_def_lines).strip()
                    match = proc_def_pattern.match(combined_lines)
                    if match:
                        proc_type = match.group(1).lower()
                        proc_name = match.group(2).lower()
                        current_proc_type = proc_type
                        current_proc_name = proc_name
                        current_proc_lines = proc_def_lines
                        i = j  # Move the main loop index to j
                        break
                    j += 1
                else:
                    # No match found in continuation lines
                    pass
        else:
            current_proc_lines.append(line)
            # Check for end of procedure
            match_end = proc_end_pattern.match(line_stripped)
            if match_end:
                end_proc_type = match_end.group(1)
                end_proc_name = match_end.group(2)
                if end_proc_type:
                    end_proc_type = end_proc_type.lower()
                if end_proc_name:
                    end_proc_name = end_proc_name.lower()
                if (end_proc_type == current_proc_type and (end_proc_name == current_proc_name or end_proc_name is None)) \
                   or (end_proc_type is None and end_proc_name is None):
                    key = (current_proc_type, current_proc_name)
                    procedure_dict[key] = current_proc_lines
                    current_proc_type = None
                    current_proc_name = None
                    current_proc_lines = []
        i += 1
    return procedure_dict

import re

def extract_procedures(lines):
    """
    Extracts subroutine and function definitions from a list of lines of Fortran code.

    This function identifies and captures Fortran subroutine and function definitions,
    including multi-line definitions with various type and attribute specifiers, such as
    "pure", "elemental", "impure", and Fortran types (e.g., real, integer, logical). It
    collects each procedure's lines until it encounters an "end" statement and stores
    them in a dictionary.

    Args:
        lines (list of str): A list of lines from a Fortran source file.

    Returns:
        dict: A dictionary where keys are tuples of the form ("subroutine", "name") or
              ("function", "name"), with "name" being the lowercase procedure name. 
              Values are lists of strings containing the lines of the procedure.
    """
    procedure_dict = {}
    current_proc_type = None
    current_proc_name = None
    current_proc_lines = []

    # Define regex pattern for procedure definitions
    proc_def_pattern = re.compile(
        r'^\s*(?!end\b)(?:[\w\s\(\),=\*\:\']+)?\b(function|subroutine)\b\s+(\w+)',
        re.IGNORECASE
    )

    # Define regex pattern for end of procedure
    proc_end_pattern = re.compile(
        r'^\s*end\b(?:\s+(function|subroutine))?(?:\s+(\w+))?',
        re.IGNORECASE
    )

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Handle line continuation with '&'
        while line.endswith('&'):
            line = line[:-1].strip() + ' ' + lines[i + 1].strip()
            i += 1
        
        if current_proc_type is None:
            # Look for procedure definition
            match = proc_def_pattern.match(line.lower())
            if match:
                # We have found a procedure definition
                proc_type = match.group(1).lower()
                proc_name = match.group(2).lower()
                current_proc_type = proc_type
                current_proc_name = proc_name
                current_proc_lines = [line]
        else:
            current_proc_lines.append(line)
            # Check for end of procedure
            match_end = proc_end_pattern.match(line.lower())
            if match_end:
                end_proc_type = match_end.group(1)
                end_proc_name = match_end.group(2)
                if end_proc_type:
                    end_proc_type = end_proc_type.lower()
                if end_proc_name:
                    end_proc_name = end_proc_name.lower()
                if (end_proc_type == current_proc_type and (end_proc_name == current_proc_name or end_proc_name is None)) \
                   or (end_proc_type is None and end_proc_name is None):
                    key = (current_proc_type, current_proc_name)
                    procedure_dict[key] = current_proc_lines
                    current_proc_type = None
                    current_proc_name = None
                    current_proc_lines = []
        i += 1
    return procedure_dict
  
if __name__ == '__main__':
    print_code = False
    src = "starpac.f90"
    with open(src, 'r') as f:
        lines = f.readlines()
    procedures = extract_procedures(lines)
    for key, proc_lines in procedures.items():
        proc_type, proc_name = key
        print(f"Procedure Type: {proc_type}, Name: {proc_name}")
        if print_code:
            print("Code:")
            print(''.join(proc_lines))
            print("\n" + "="*80 + "\n")
