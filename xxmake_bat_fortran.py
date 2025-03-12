#!/usr/bin/env python3
"""
Create a GNU Makefile given:
  1) the name of a compiler (g95, gfortran, ifort, nag, lf95, etc.)
  2) one or more files containing lists of source files (list_files)

A list file could like

kind.f90
xkind.f90

Usage:
  python xxmake_bat_fortran.py <compiler> <list_file1> <list_file2> ...

The last source file in each list file is treated as the main program.
The executable is named after the main program, with the compiler abbreviation appended.

Generates a Makefile named: mk_[compiler]_combined.mk
"""

import sys
from strip_suffix import strip_suffix

# --- Step 1: Parse Command-Line Arguments ---
if len(sys.argv) < 3:
    print("Usage: python create_gnu_make.py <compiler> <list_file1> <list_file2> ...")
    sys.exit(1)

# The first argument is the compiler
compiler = sys.argv[1]

# The remaining arguments are list files
list_files = sys.argv[2:]

# Handle Intel compiler synonyms
if compiler == "intel":
    compiler = "ifort"

# We'll store recognized compilers and their typical options
test_gfortran = False

if compiler == "g95":
    opt = "-Wall -Wextra -Wimplicit-none -Werror=100,113,115,137,146,147,159,163 -ftrace=full -fbounds-check -freal=nan -fmodule-private -Wno=112,167"
    cmpl_abbrev = "g95"
elif compiler == "gfortran":
    if test_gfortran:
        opt = "-O0"
    else:
        opt = "-O0 -Wall -Werror=unused-parameter -Werror=unused-variable -Werror=unused-function -Wno-maybe-uninitialized -Wno-surprising -fbounds-check -static -g -fmodule-private"
    cmpl_abbrev = "gfort"
elif compiler in ["ifort", "intel"]:
    opt = "-fast -warn all -debug full -check bounds -diag-disable 8290,8291"
    cmpl_abbrev = "ifort"
elif compiler == "lf95":
    opt = "-nco -chk -g -stchk -trace -nsav -trap diou -lst -w -o0"
    cmpl_abbrev = "lf95"
elif compiler == "nf95" or compiler == "nag":
    opt = "-C -C=undefined -nan -w=all -gline -info"
    cmpl_abbrev = "nag"
else:
    opt = "-O2"
    cmpl_abbrev = compiler

# Decide on Makefile name
make_file = "mk_" + compiler + "_combined.mk"

# --- Step 2: Read Source Files ---
src_suffix = ".f90"
all_srcs = set()  # Use a set to avoid duplicates
obj_to_exe = {}   # Map object files to executables
exe_names = []    # List of executable names

for list_file in list_files:
    try:
        with open(list_file, "r") as fp:
            srcs = [line.strip() for line in fp if line.strip()]
    except FileNotFoundError:
        list_file_alt = list_file + "_files.txt"
        with open(list_file_alt, "r") as fp:
            srcs = [line.strip() for line in fp if line.strip()]

    # The last file in the list is the main program
    main_program = srcs[-1]
    main_base = strip_suffix(main_program, src_suffix)
    if not main_base:
        main_base = main_program  # Fallback if no .f90 suffix
    exe_name = main_base + "_" + cmpl_abbrev + ".exe"
    exe_names.append(exe_name)

    # Strip .f90 suffix from each line if present
    for xfile in srcs:
        xbase = strip_suffix(xfile, src_suffix)
        if xbase:
            obj_file = xbase + ".o"
            all_srcs.add(xfile)
            if obj_file in obj_to_exe:
                obj_to_exe[obj_file].append(exe_name)
            else:
                obj_to_exe[obj_file] = [exe_name]

# --- Step 3: Write the GNU Makefile ---
with open(make_file, "w") as outp:
    # Define executables
    print(f"executables = {' '.join(exe_names)}", file=outp)
    print(f"FC     = {compiler}", file=outp)  # Fortran compiler variable
    print(f"FFLAGS = {opt}", file=outp)       # Fortran flags

    # Define object files
    obj_list = list(obj_to_exe.keys())
    print(f"obj    = {' '.join(obj_list)}", file=outp)

    # Default target: build all executables
    print("\nall: $(executables)\n", file=outp)

    # Pattern rule: .f90 -> .o
    print("# Compile .f90 to .o", file=outp)
    print("%.o: %.f90", file=outp)
    print("\t$(FC) $(FFLAGS) -c $<\n", file=outp)

    # Rules for linking executables
    for exe_name in exe_names:
        # Find object files required for this executable
        required_objs = [obj for obj, exes in obj_to_exe.items() if exe_name in exes]
        print(f"{exe_name}: {' '.join(required_objs)}", file=outp)
        print(f"\t$(FC) -o {exe_name} {' '.join(required_objs)} $(FFLAGS)\n", file=outp)

    # run target (runs all executables)
    print("run: $(executables)", file=outp)
    for exe_name in exe_names:
        print(f"\t./{exe_name}", file=outp)
    print("", file=outp)

    # clean target
    print("clean:", file=outp)
    print("\trm -f $(executables) $(obj)\n", file=outp)

print(f"Created GNU Makefile: {make_file}")
