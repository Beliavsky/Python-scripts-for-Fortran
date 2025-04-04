import sys
import re

def add_implicit_none(fortran_file, output_file=None):
    """
    Reads a Fortran source file and adds 'implicit none' to subroutines/functions
    that don't have it, placing it after 'use' statements and before declarations
    with proper alignment.
    
    Args:
        fortran_file (str): Path to input Fortran source file
        output_file (str, optional): Path to output file. If None, prints to console
    """
    # Read the input file
    with open(fortran_file, 'r') as f:
        lines = [line.rstrip() for line in f.readlines()]  # Remove trailing whitespace
    
    # Process the file
    output_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for subroutine/function start
        if (line.strip().lower().startswith('subroutine') or 
            line.strip().lower().startswith('function')):
            # Collect the entire routine
            routine_lines = [line]
            i += 1
            has_implicit_none = False
            last_use_idx = -1
            first_decl_idx = -1
            decl_indent = None
            
            # Get base indentation from subroutine/function line
            base_indent = len(line) - len(line.lstrip())
            
            # Process the routine body
            while i < len(lines) and not lines[i].strip().lower().startswith('end '):
                curr_line = lines[i]
                routine_lines.append(curr_line)
                
                # Check for implicit none with variable spacing (case-insensitive)
                if re.search(r'implicit\s+none', curr_line.lower()):
                    has_implicit_none = True
                
                # Track last use statement
                if curr_line.strip().lower().startswith('use'):
                    last_use_idx = len(routine_lines) - 1
                
                # Track first declaration and its indentation
                elif (curr_line.strip().lower().startswith('real') or
                      curr_line.strip().lower().startswith('integer') or
                      curr_line.strip().lower().startswith('character') or
                      curr_line.strip().lower().startswith('logical')):
                    if first_decl_idx == -1:
                        first_decl_idx = len(routine_lines) - 1
                        decl_indent = len(curr_line) - len(curr_line.lstrip())
                
                i += 1
            
            # Add the end statement
            if i < len(lines):
                routine_lines.append(lines[i])
                i += 1
            
            # Add implicit none if not present
            if not has_implicit_none:
                insert_idx = last_use_idx + 1 if last_use_idx >= 0 else 1
                # Use declaration indent if available, otherwise base_indent + 4
                target_indent = decl_indent if decl_indent is not None else base_indent + 4
                implicit_line = ' ' * target_indent + 'implicit none'
                routine_lines.insert(insert_idx, implicit_line)
            
            # Add the processed routine to output
            output_lines.extend(routine_lines)
            
            # Add following blank lines or comments if they exist
            while (i < len(lines) and 
                   (not lines[i].strip() or lines[i].strip().startswith('!'))):
                output_lines.append(lines[i])
                i += 1
        else:
            # Copy non-routine lines as is
            output_lines.append(line)
            i += 1
    
    # Remove trailing blank lines
    while output_lines and not output_lines[-1].strip():
        output_lines.pop()
    
    # Write output
    output_text = '\n'.join(output_lines) + '\n'
    if output_file:
        with open(output_file, 'w') as f:
            f.write(output_text)
    else:
        print(output_text)

if __name__ == "__main__":
    # Check if command line argument is provided
    if len(sys.argv) != 2:
        print("Usage: python script.py <fortran_source_file>")
        sys.exit(1)
    
    # Get the source file from command line argument
    source_file = sys.argv[1]
    
    # Process the file
    try:
        add_implicit_none(source_file)
    except FileNotFoundError:
        print(f"Error: File '{source_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        sys.exit(1)
