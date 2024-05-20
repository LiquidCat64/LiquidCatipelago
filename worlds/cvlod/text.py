from typing import Tuple

cvlod_char_dict = {"\n": (0xB6, 0), " ": (0xB7,  8), "!": (0x01,  4), '"': (0x02,  7), "#": (0x03, 10), "$": (0x04, 10),
                   "%": (0x05, 14), "&": (0x06, 10), "'": (0x07,  5), "(": (0x08,  6), ")": (0x09,  6), "*": (0x0A,  8),
                   "+": (0x0B, 10), ",": (0x0C,  5), "-": (0x0D,  6), ".": (0x0E,  5), "/": (0x0F, 10), "0": (0x10,  8),
                   "1": (0x11,  7), "2": (0x12,  8), "3": (0x13,  9), "4": (0x14,  9), "5": (0x15,  9), "6": (0x16, 10),
                   "7": (0x17,  9), "8": (0x18, 10), "9": (0x19,  9), ":": (0x1A,  5), ";": (0x1B,  6), "<": (0x1C, 10),
                   "=": (0x1D, 10), ">": (0x1E, 10), "?": (0x1F, 11), "@": (0x20, 13), "A": (0x21, 14), "B": (0x22, 11),
                   "C": (0x23, 12), "D": (0x24, 12), "E": (0x25, 10), "F": (0x26,  8), "G": (0x27, 13), "H": (0x28, 14),
                   "I": (0x29,  5), "J": (0x2A,  7), "K": (0x2B, 12), "L": (0x2C,  9), "M": (0x2D, 10), "N": (0x2E, 13),
                   "O": (0x2F, 13), "P": (0x30, 10), "Q": (0x31, 14), "R": (0x32, 11), "S": (0x33,  9), "T": (0x34, 10),
                   "U": (0x35, 14), "V": (0x36, 11), "W": (0x37, 16), "X": (0x38, 12), "Y": (0x39, 10), "Z": (0x3A, 11),
                   "[": (0x3B,  6), "\\": (0x3C, 9), "]": (0x3D,  7), "^": (0x3E,  9), "_": (0x3F, 10), "`": (0x40,  6),
                   "a": (0x41,  9), "b": (0x42,  9), "c": (0x43,  8), "d": (0x44,  9), "e": (0x45,  9), "f": (0x46,  7),
                   "g": (0x47,  9), "h": (0x48,  9), "i": (0x49,  6), "j": (0x4A,  5), "k": (0x4B,  9), "l": (0x4C,  6),
                   "m": (0x4D, 13), "n": (0x4E, 10), "o": (0x4F, 10), "p": (0x50,  9), "q": (0x51,  9), "r": (0x52,  7),
                   "s": (0x53,  8), "t": (0x54,  6), "u": (0x55,  8), "v": (0x56, 10), "w": (0x57, 14), "x": (0x58, 10),
                   "y": (0x59,  9), "z": (0x5A,  9), "{": (0x5B,  7), "|": (0x5C,  5), "}": (0x5D,  8), "~": (0x5E,  9),
                   "◊": (0x5F,  7), "「": (0x60, 7), "」": (0x61,  7), "。": (0x62, 5), "•": (0x63,  5), "—": (0x64,  9),
                   "▶": (0x65,  6), "₀": (0x66,  6), "₁": (0x67,  4), "₂": (0x68,  6), "₃": (0x69,  6), "₄": (0x6A,  6),
                   "₅": (0x6B,  6), "₆": (0x6C,  6), "₇": (0x6D,  6), "₈": (0x6E,  6), "₉": (0x6F,  6), "〃": (0x70,  6),
                   "°": (0x71,  5), "∞": (0x72, 16), "、": (0x73,  7)}
# [0] = CVLoD's in-game ID for that text character.
# [1] = How much space towards the in-game line length limit it contributes.


def cvlod_string_to_bytearray(cvlodtext: str, a_advance: bool = False, append_end: bool = True) -> bytearray:
    """Converts a string into a list of bytes following cvlod's string format."""
    text_bytes = bytearray(0)
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
        if cvlodtext[i] in cvlod_char_dict:
            line_len += cvlod_char_dict[cvlodtext[i]][1]
        else:
            line_len += 11

        if line_len > textbox_len_limit:
            return cvlodtext[0x00:i]

    return cvlodtext


def cvlod_text_wrap(cvlodtext: str, textbox_len_limit: int) -> Tuple[str, int]:
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
            line_len += 8
        else:
            word_divider = ""

        for char in words[i]:
            if char in cvlod_char_dict:
                line_len += cvlod_char_dict[char][1]
                word_len += cvlod_char_dict[char][1]
            else:
                line_len += 11
                word_len += 11

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
