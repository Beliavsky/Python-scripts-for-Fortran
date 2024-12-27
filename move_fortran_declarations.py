"""
A tool for fixing Fortran code by moving all declarations to the correct position.

This module provides functionality to reorganize Fortran code to ensure proper ordering of statements:
1. PROGRAM/SUBROUTINE/FUNCTION statement
2. USE and IMPLICIT statements 
3. Variable declarations
4. Executable statements

The main class FortranDeclarationFixer identifies and correctly positions declarations using regular 
expressions to parse different Fortran constructs. It preserves program structure including internal
subprograms and maintains original formatting.

Example:
   fixer = FortranDeclarationFixer()
   fixed_code = fixer.fix_fortran_code(fortran_code)
"""

import re
from typing import List, Tuple

class FortranDeclarationFixer:
    def __init__(self):
        # Regular expressions for different Fortran constructs
        self.declaration_pattern = re.compile(
            r'^\s*(?:real|integer|logical|character|complex|type|class)\s*(?:\([^)]+\))?\s*(?:::)?\s*[:\w,\s()*]+',
            re.IGNORECASE
        )
        self.program_start = re.compile(r'^\s*program\s+\w+', re.IGNORECASE)
        self.subroutine_start = re.compile(r'^\s*(?:pure\s+)?subroutine\s+\w+', re.IGNORECASE)
        self.function_start = re.compile(r'^\s*(?:pure\s+)?function\s+\w+', re.IGNORECASE)
        self.contains_stmt = re.compile(r'^\s*contains\s*$', re.IGNORECASE)
        self.use_stmt = re.compile(r'^\s*use\s+\w+', re.IGNORECASE)
        self.implicit_stmt = re.compile(r'^\s*implicit\s+none', re.IGNORECASE)
        self.module_start = re.compile(r'^\s*module\s+\w+', re.IGNORECASE)
        self.end_stmt = re.compile(r'^\s*end\s*(?:program|subroutine|function|module)?\s*\w*', re.IGNORECASE)

    def is_declaration(self, line: str) -> bool:
        """Check if a line is a declaration statement."""
        return bool(self.declaration_pattern.match(line))

    def is_use_or_implicit(self, line: str) -> bool:
        """Check if a line is a USE or IMPLICIT statement."""
        return bool(self.use_stmt.match(line) or self.implicit_stmt.match(line))

    def is_program_unit_start(self, line: str) -> bool:
        """Check if line starts a program unit."""
        return bool(
            self.program_start.match(line) or
            self.subroutine_start.match(line) or
            self.function_start.match(line) or
            self.module_start.match(line)
        )

    def fix_program_unit(self, lines: List[str]) -> List[str]:
        """Fix declarations in a single program unit."""
        # Initialize sections
        unit_header = []  # For PROGRAM/SUBROUTINE/FUNCTION statement
        use_implicit_stmts = []
        declarations = []
        executable_stmts = []
        internal_subprograms = []

        # First line should be the program unit start
        if lines and self.is_program_unit_start(lines[0]):
            unit_header = [lines[0]]
            lines = lines[1:]
        
        found_contains = False
        
        for line in lines:
            if self.contains_stmt.match(line):
                found_contains = True
                internal_subprograms.append(line)
            elif found_contains:
                internal_subprograms.append(line)
            elif self.is_use_or_implicit(line):
                use_implicit_stmts.append(line)
            elif self.is_declaration(line):
                declarations.append(line)
            else:
                executable_stmts.append(line)

        # Combine sections in correct order
        result = (
            unit_header +  # PROGRAM/SUBROUTINE/FUNCTION statement first
            use_implicit_stmts +  # USE and IMPLICIT statements next
            declarations +  # Variable declarations
            executable_stmts  # Executable statements
        )
        
        if internal_subprograms:
            result.extend(internal_subprograms)

        return result

    def split_into_program_units(self, lines: List[str]) -> List[List[str]]:
        """Split Fortran code into separate program units."""
        units = []
        current_unit = []
        
        for line in lines:
            if self.is_program_unit_start(line):
                if current_unit:  # If we have a previous unit
                    units.append(current_unit)
                current_unit = [line]
            else:
                current_unit.append(line)
        
        if current_unit:
            units.append(current_unit)
            
        return units

    def fix_fortran_code(self, code: str) -> str:
        """Fix all declarations in Fortran code."""
        # Split into lines and remove empty lines
        lines = [line.rstrip() for line in code.splitlines() if line.strip()]
        
        # Split into program units
        program_units = self.split_into_program_units(lines)
        
        # Fix each program unit
        fixed_units = []
        for unit in program_units:
            fixed_unit = self.fix_program_unit(unit)
            fixed_units.extend(fixed_unit)
        
        # Combine everything back
        return '\n'.join(fixed_units)

# Example usage
def main():
    # Read input file
    with open('input.f90', 'r') as f:
        code = f.read()
    
    # Fix declarations
    fixer = FortranDeclarationFixer()
    fixed_code = fixer.fix_fortran_code(code)
    
    # Write output file
    with open('output.f90', 'w') as f:
        f.write(fixed_code)

if __name__ == '__main__':
    main()
