import re

def remove_fortran_continuations(code):
    """Convert Fortran continuation lines into single lines."""
    lines = code.splitlines()
    result = []
    buffer = ""

    for line in lines:
        # Strip leading/trailing whitespace
        stripped_line = line.strip()

        # Find continuation outside quotes
        if re.search(r'&(?=(?:[^\'\"]|\'[^\']*\'|"[^"]*")*$)', stripped_line):
            # Remove the continuation character and append the line to the buffer
            buffer += re.sub(r'&(?=(?:[^\'\"]|\'[^\']*\'|"[^"]*")*$)', '', stripped_line).strip()
        else:
            # Append the line to the buffer and add the buffer to results
            buffer += stripped_line
            result.append(buffer)
            buffer = ""

    # Add any remaining buffer content
    if buffer:
        result.append(buffer)

    return "\n".join(result)

# Example usage
fortran_code = """implicit none
integer :: i, &
j
print*,\"hello\", &
   \" world\"
end"""

converted_code = remove_fortran_continuations(fortran_code)
print("original code:\n" + fortran_code)
print("\nconverted code:\n" + converted_code)
