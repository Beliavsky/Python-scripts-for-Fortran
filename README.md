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
