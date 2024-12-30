# Python scripts for Fortran
Python scripts to fix, analyze and reformat Fortran code

`fortran_procedures.py` has the function

```
def extract_procedures(lines):
    """ Extracts subroutine and function definitions from a list of lines of Fortran code. """
```

`xxsplit_fortran_line.py` has the function
```
def split_fortran_line(line):
    """ Splits a Fortran line into code and comment parts, ignoring '!' inside quotes. """
```

`move_fortran_declarations.py` is a tool by ClaudeAI for fixing Fortran code by moving declarations
before executable statements. ChatGPT o1 can produce code that needs such a fix.

`xremove_fortran_continuations.py` has the function
```
def remove_fortran_continuations(code):
    """Convert Fortran continuation lines into single lines."""
```
