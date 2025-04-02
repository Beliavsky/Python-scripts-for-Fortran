def strip_suffix(string,suffix):
    if (string.endswith(suffix)):
        return string[:-len(suffix)]
    else:
        return string
        