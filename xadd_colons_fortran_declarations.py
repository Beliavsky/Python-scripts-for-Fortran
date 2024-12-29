import re

def add_colon_to_declarations(code):
    """Add :: to Fortran declarations that do not have it."""
    declaration_patterns = [
        r'(?i)\b(integer|real|logical|character)\b(?!\s*::|.*?,\s*dimension\s*\()',
    ]
    lines = code.splitlines()
    result = []

    for line in lines:
        modified = line
        for pattern in declaration_patterns:
            # Add :: to declarations missing it, skipping lines with dimension before ::
            modified = re.sub(pattern, r'\1 ::', modified)
        result.append(modified)
    return "\n".join(result)

# Example usage
fortran_code = """implicit none
integer i
integer :: j
integer k(3)
logical b
real :: pi=3.14
integer, dimension(5) :: ii
real x, y, &
   z
z = 3.1
i = 2
j = 4
k = i+j
print*,k
b = .true.
print*,b
print*,pi
ii = j
print*,ii
print*,"z=", z
end"""

converted_code = add_colon_to_declarations(fortran_code)
print("original code:\n" + fortran_code)
print("\nconverted code:\n" + converted_code)
