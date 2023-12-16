cvlod_char_dict = {"\n": [0xB6, 0], " ": [0xB7, 4], "!": [0x01, 2], '"': [0x02, 5], "#": [0x03, 6], "$": [0x04, 5],
                   "%": [0x05, 8], "&": [0x06, 7], "'": [0x07, 4], "(": [0x08, 3], ")": [0x09, 3], "*": [0x0A, 4],
                   "+": [0x0B, 5], ",": [0x0C, 3], "-": [0x0D, 4], ".": [0x0E, 3], "/": [0x0F, 6], "0": [0x10, 5],
                   "1": [0x11, 3], "2": [0x12, 5], "3": [0x13, 4], "4": [0x14, 5], "5": [0x15, 5], "6": [0x16, 5],
                   "7": [0x17, 5], "8": [0x18, 5], "9": [0x19, 5], ":": [0x1A, 3], ";": [0x1B, 3], "<": [0x1C, 3],
                   "=": [0x1D, 4], ">": [0x1E, 3], "?": [0x1F, 5], "@": [0x20, 8], "A": [0x21, 7], "B": [0x22, 6],
                   "C": [0x23, 5], "D": [0x24, 7], "E": [0x25, 5], "F": [0x26, 6], "G": [0x27, 6], "H": [0x28, 7],
                   "I": [0x29, 3], "J": [0x2A, 3], "K": [0x2B, 6], "L": [0x2C, 6], "M": [0x2D, 8], "N": [0x2E, 7],
                   "O": [0x2F, 6], "P": [0x30, 6], "Q": [0x31, 8], "R": [0x32, 6], "S": [0x33, 5], "T": [0x34, 6],
                   "U": [0x35, 6], "V": [0x36, 7], "W": [0x37, 8], "X": [0x38, 6], "Y": [0x39, 7], "Z": [0x3A, 6],
                   "[": [0x3B, 3], "\\": [0x3C, 6], "]": [0x3D, 3], "^": [0x3E, 6], "_": [0x3F, 5], "`": [0x40, 5],
                   "a": [0x41, 5], "b": [0x42, 6], "c": [0x43, 4], "d": [0x44, 6], "e": [0x45, 5], "f": [0x46, 5],
                   "g": [0x47, 5], "h": [0x48, 6], "i": [0x49, 3], "j": [0x4A, 3], "k": [0x4B, 6], "l": [0x4C, 3],
                   "m": [0x4D, 8], "n": [0x4E, 6], "o": [0x4F, 5], "p": [0x50, 5], "q": [0x51, 5], "r": [0x52, 4],
                   "s": [0x53, 4], "t": [0x54, 4], "u": [0x55, 5], "v": [0x56, 6], "w": [0x57, 8], "x": [0x58, 5],
                   "y": [0x59, 5], "z": [0x5A, 4], "{": [0x5B, 4], "|": [0x5C, 2], "}": [0x5D, 3], "~": [0x5E, 4],
                   "◊": [0x5F, 4], "「": [0x60, 3], "」": [0x61, 3], "。": [0x62, 3], "•": [0x63, 3], "—": [0x64, 4],
                   "▶": [0x65, 4], "₀": [0x66, 4], "₁": [0x67, 4], "₂": [0x68, 4], "₃": [0x69, 4], "₄": [0x6A, 4],
                   "₅": [0x6B, 4], "₆": [0x6C, 4], "₇": [0x6D, 4], "₈": [0x6E, 4], "₉": [0x6F, 4], "〃": [0x70, 3],
                   "°": [0x71, 3], "∞": [0x72, 8], "、": [0x73, 8]}


# [0] = CVLoD's in-game ID for that text character.
# [1] = How much space towards the in-game line length limit it contributes.


def cvlod_string_to_bytes(cvlodtext: str, a_advance: bool = False, append_end: bool = True) -> list:
    """Converts a string into a list of bytes following cvlod's string format."""
    text_bytes = []
    for i, char in enumerate(cvlodtext):
        if char == "\t":
            text_bytes.extend([0xFF, 0xFF])
        else:
            if char in cvlod_char_dict:
                if cvlod_char_dict[char][0] >= 0xB0:
                    text_bytes.extend([cvlod_char_dict[char][0], 0x00])
                else:
                    text_bytes.extend([0x00, cvlod_char_dict[char][0]])
            else:
                text_bytes.extend([0x00, 0x41])

    if a_advance:
        text_bytes.extend([0xA3, 0x00])
    if append_end:
        text_bytes.extend([0xFF, 0xFF])
    return text_bytes


def cvlod_text_truncate(cvlodtext: str, textbox_len_limit: int) -> str:
    """Truncates a string at a given in-game text line length."""
    line_len = 0

    for i in range(len(cvlodtext)):
        line_len += cvlod_char_dict[cvlodtext[i]][1]

        if line_len > textbox_len_limit:
            return cvlodtext[0x00:i]

    return cvlodtext


def cvlod_text_wrap(cvlodtext: str, textbox_len_limit: int) -> tuple:
    """Rebuilds a string with some of its spaces replaced with newlines to ensure the text wraps properly in an in-game
    textbox of a given length."""
    words = cvlodtext.split(" ")
    new_text = ""
    line_len = 0
    num_lines = 1

    for i in range(len(words)):
        word_len = 0
        word_divider = " "

        if line_len != 0:
            line_len += 4
        else:
            word_divider = ""

        for char in words[i]:
            if char in cvlod_char_dict:
                line_len += cvlod_char_dict[char][1]
                word_len += cvlod_char_dict[char][1]
            else:
                line_len += 5
                word_len += 5

            if word_len > textbox_len_limit or char in ["\n", "\t"]:
                word_len = 0
                line_len = 0
                if num_lines < 4:
                    num_lines += 1

            if line_len > textbox_len_limit:
                word_divider = "\n"
                line_len = word_len
                if num_lines < 4:
                    num_lines += 1

        new_text += word_divider + words[i]

    return new_text, num_lines
