import subprocess
import re
import argparse
import os
from collections import defaultdict

def run_nm(file_path):
    """
    Run the 'nm' command on the specified object file and return its output.
    
    Args:
        file_path (str): Path to the object file (e.g., 'myfile.o')
    
    Returns:
        str: Output of the nm command, or None if an error occurs
    """
    try:
        result = subprocess.run(['nm', '--defined-only', '--demangle', file_path], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running nm on {file_path}: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Error: 'nm' command not found. Ensure nm is installed and in your PATH.")
        return None

def extract_fortran_symbols(nm_output):
    """
    Extract function/subroutine names from nm output.
    
    Args:
        nm_output (str): Raw output from the nm command
    
    Returns:
        list: List of cleaned function/subroutine names
    """
    if not nm_output:
        return []

    lines = nm_output.strip().split('\n')
    symbols = []
    pattern = re.compile(r'^\w+\s+T\s+(.+)$')

    for line in lines:
        match = pattern.match(line.strip())
        if match:
            symbol = match.group(1)
            cleaned_symbol = symbol.rstrip('_')
            if cleaned_symbol:
                symbols.append(cleaned_symbol)

    return symbols

def get_symbol_file_map(max_files=None):
    """
    Return a dictionary mapping symbols to lists of object files they are defined in.
    
    Args:
        max_files (int, optional): Maximum number of object files to process. If None, process all.
    
    Returns:
        dict: Dictionary with keys as symbol names and values as lists of object file paths.
    """
    # Dictionary to store symbol -> list of object files
    symbol_to_files = defaultdict(list)
    file_count = 0

    # Walk through current directory and subdirectories
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.o'):  # Check for .o files
                if max_files is not None and file_count >= max_files:
                    break
                
                file_path = os.path.join(root, file)
                nm_output = run_nm(file_path)
                if nm_output:
                    symbols = extract_fortran_symbols(nm_output)
                    for symbol in symbols:
                        symbol_to_files[symbol].append(file_path)
                    file_count += 1

        if max_files is not None and file_count >= max_files:
            break

    # Convert defaultdict to regular dict for return
    return dict(symbol_to_files)

def find_duplicate_symbols(max_files=None):
    """
    Find and report symbols defined in multiple .o files in the current directory and subdirectories.
    List symbols in descending order of the number of files they appear in.
    
    Args:
        max_files (int, optional): Maximum number of object files to process. If None, process all.
    """
    # Use the new function to get the symbol-to-files mapping
    symbol_to_files = get_symbol_file_map(max_files)

    # Filter and sort symbols by number of files (descending order)
    duplicates = [(symbol, files) for symbol, files in symbol_to_files.items() if len(files) > 1]
    duplicates.sort(key=lambda x: len(x[1]), reverse=True)  # Sort by number of files, descending

    # Print results
    if duplicates:
        for symbol, files in duplicates:
            print(f"{symbol} (found in {len(files)} object files):")
            for file in files:
                print(f"  {file}")
            print()  # Blank line between entries
    else:
        print("No symbols found in more than one object file.")

    if max_files is not None and len(symbol_to_files) > 0 and max_files <= file_count:
        print(f"Note: Analysis limited to {max_files} files; results may be incomplete.")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Extract defined symbols from object files or find duplicates.")
    parser.add_argument('object_file', nargs='?', help="Path to a single object file (optional)")
    parser.add_argument('--duplicates', action='store_true', 
                        help="Find symbols defined in multiple .o files in current directory and subdirectories")
    parser.add_argument('--max-files', type=int, default=None, 
                        help="Limit the number of object files processed with --duplicates or no arguments")
    args = parser.parse_args()

    if args.object_file and not args.duplicates:
        # Single-file mode
        nm_output = run_nm(args.object_file)
        if nm_output is None:
            return
        symbols = extract_fortran_symbols(nm_output)
        if symbols:
            print(f"Defined functions and subroutines in {args.object_file}:")
            for symbol in symbols:
                print(f" - {symbol}")
        else:
            print(f"No defined functions or subroutines found in {args.object_file}.")
    else:
        # Default to finding duplicates if no arguments, or if --duplicates is specified
        max_files = args.max_files if args.max_files is not None else None
        find_duplicate_symbols(max_files=max_files)

if __name__ == "__main__":
    main()
