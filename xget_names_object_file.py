import subprocess
import re
import argparse

def run_nm(file_path):
    """
    Run the 'nm' command on the specified object file and return its output.
    
    Args:
        file_path (str): Path to the object file (e.g., 'myfile.o')
    
    Returns:
        str: Output of the nm command, or None if an error occurs
    """
    try:
        # Run nm with --defined-only to get only defined symbols
        result = subprocess.run(['nm', '--defined-only', file_path], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running nm: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Error: 'nm' command not found. Ensure nm is installed and in your PATH.")
        return None

def extract_fortran_symbols(nm_output):
    """
    Extract Fortran function and subroutine names from nm output.
    
    Args:
        nm_output (str): Raw output from the nm command
    
    Returns:
        list: List of cleaned function/subroutine names
    """
    if not nm_output:
        return []

    # Split the output into lines
    lines = nm_output.strip().split('\n')
    symbols = []

    # Regular expression to match lines with defined symbols (T for text section)
    # Example line: "00000000 T mysub_"
    pattern = re.compile(r'^\w+\s+T\s+(.+)$')

    for line in lines:
        match = pattern.match(line.strip())
        if match:
            symbol = match.group(1)
            # Clean up Fortran name mangling (remove trailing underscore(s))
            cleaned_symbol = symbol.rstrip('_')
            if cleaned_symbol:  # Ensure it's not empty after cleaning
                symbols.append(cleaned_symbol)
    return symbols

def main():
    # Set up argument parser for command-line input
    parser = argparse.ArgumentParser(description="Extract defined Fortran symbols from an object file.")
    parser.add_argument('object_file', help="Path to the Fortran object file (e.g., myfile.o)")
    args = parser.parse_args()

    # Get the object file path from the arguments
    object_file = args.object_file

    # Run nm and get the output
    nm_output = run_nm(object_file)
    if nm_output is None:
        return

    # Extract and clean the Fortran symbols
    symbols = extract_fortran_symbols(nm_output)

    # Print the results
    if symbols:
        print(f"Defined functions and subroutines in {object_file}:")
        for symbol in symbols:
            print(f" - {symbol}")
    else:
        print(f"No defined functions or subroutines found in {object_file}.")

if __name__ == "__main__":
    main()
