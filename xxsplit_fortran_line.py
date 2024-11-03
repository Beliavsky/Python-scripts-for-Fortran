def split_fortran_line(line):
    """
    Splits a Fortran line into code and comment parts, ignoring '!' inside quotes.
    
    Args:
        line (str): A line of Fortran code.
        
    Returns:
        tuple: A 2-element tuple (code, comment), where 'comment' is None if there is no comment.
    """
    in_single_quote = False
    in_double_quote = False
    comment_pos = None
    # Loop through each character to identify unquoted '!'
    for i, char in enumerate(line):
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        elif char == '!' and not in_single_quote and not in_double_quote:
            comment_pos = i
            break
    # Split code and comment based on identified position of '!'
    if comment_pos is not None:
        code = line[:comment_pos].rstrip()
        comment = line[comment_pos:].lstrip()
    else:
        code = line
        comment = None
    if code == "":
        code = None
    return code, comment

src = "hello.f90" # 
lines = open(src, "r").readlines()
stripped_source_file = "temp.f90" # if not None, file to which comment-free code is written
outp = open(stripped_source_file, "w")
for line in lines:
    line = line.rstrip()
    code, comment = split_fortran_line(line)
    print("\nline: " + line)
    if code is not None:
        print("code: " + code)
        if stripped_source_file:
            print(code.rstrip(), file=outp)
    if comment is not None:
        print("comment: " + comment)
