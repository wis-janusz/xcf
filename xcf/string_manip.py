def remove_symbols(s):
    s_out = ""
    for char in s:
        if char.isalnum() or char == " ":
            s_out += char
    return s_out


def remove_nonalnum(s):
    s_out = ""
    for char in s:
        if char.isalnum():
            s_out += char
    return s_out
