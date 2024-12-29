import re

def split_fortran_statements(code):
    """Split Fortran statements separated by semicolons into separate lines."""
    lines = code.splitlines()
    result = []

    for line in lines:
        # Split by semicolons outside quotes
        statements = re.split(r';(?=(?:[^\'\"]|\'[^\']*\'|"[^"]*")*$)', line)
        # Add each statement as a separate line, stripped of extra whitespace
        result.extend(stmt.strip() for stmt in statements if stmt.strip())

    return "\n".join(result)

# Example usage
fortran_code = """implicit none
integer :: i, j
i = 2 ; j = 3; print*,\"i;j;i*j\",i,j,i*j
end"""

converted_code = split_fortran_statements(fortran_code)
print("original code:\n" + fortran_code)
print("\nconverted code:\n" + converted_code)
