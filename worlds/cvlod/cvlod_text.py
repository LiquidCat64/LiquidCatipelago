import logging

CVLOD_CHAR_WIDTHS = {" ": 8, "!": 4, '"': 7, "#": 10, "$": 10, "%": 14, "&": 10, "'": 5, "(": 6, ")": 6, "*": 8,
                     "+": 10, ",": 5, "-": 6, ".": 5, "/": 10, "0": 8, "1": 7, "2": 8, "3": 9, "4": 9, "5": 9, "6": 10,
                     "7": 9, "8": 10, "9": 9, ":": 5, ";": 6, "<": 10, "=": 10, ">": 10, "?": 11, "@": 13, "A": 14,
                     "B": 11, "C": 12, "D": 12, "E": 10, "F": 8, "G": 13, "H": 14, "I": 5, "J": 7, "K": 12, "L": 9,
                     "M": 16, "N": 13, "O": 13, "P": 10, "Q": 14, "R": 11, "S": 9, "T": 10, "U": 14, "V": 11, "W": 16,
                     "X": 12, "Y": 10, "Z": 11, "[": 6, "\\": 9, "]": 7, "^": 9, "_": 10, "`": 6, "a": 9, "b": 9,
                     "c": 8, "d": 9, "e": 9, "f": 7, "g": 9, "h": 9, "i": 6, "j": 5, "k": 9, "l": 6, "m": 13, "n": 10,
                     "o": 10, "p": 9, "q": 9, "r": 7, "s": 8, "t": 6, "u": 8, "v": 10, "w": 14, "x": 10, "y": 9, "z": 9,
                     "{": 7, "|": 5, "}": 8, "~": 9, "◊": 7, "「": 7, "」": 7, "。": 5, "•": 5, "—": 9, "▷": 6, "₀": 6,
                     "₁": 4, "₂": 6, "₃": 6, "₄": 6, "₅": 6, "₆": 6, "₇": 6, "₈": 6, "₉": 6, "〃": 6, "°": 5, "∞": 16,
                     "、": 7, "◆": 12}

CVLOD_DEFAULT_CHAR = "?"
CVLOD_ASCII_DIFFERENCE = 0x20
CVLOD_STRING_END_CHARACTER = b"\xFF\xFF"
CVLOD_TEXT_POOL_END_CHARACTER = b"\xB5\x00"

CVLOD_COMMAND_CHARS = {"↗": 0xA0,  # Jump ahead to a corresponding 0xA1 character in the text pool. Arg = Which one.
                       "↘": 0xA1,  # Spot to jump to from a corresponding 0xA0 character. Arg = Which one.
                       "✨":  0xA2,  # Toggle yellow text.
                       "🅰": 0xA3,  # Make the player press A to advance past here. Arg = Instead auto-advance after
                                    # that number of frames if not 0.
                       "⬘": 0xA7,  # Pin a string on the current text line, typically a speaking character's name.
                                   # Arg = Pin if 0, unpin if 1.
                       "▶": 0xAA,  # Start set of selectable options text. Arg = Default option ID.
                       "◆": 0xAB,  # Start of selectable option. Arg = option ID.
                       "◀": 0xAC,  # End set of selectable options text.
                       "👉": 0xAD,  # Start player character-exclusive text. Arg = character ID.
                       "👈": 0xAE,  # End player character-exclusive text.
                       "⏸": 0xAF,  # Pause text and insert newline. Arg = How many frames to wait on.
                       "\f": 0xB2,  # Clear the text currently in the textbox (without closing it).
                       "\r": 0xB5,  # End of the ENTIRE text pool. There should be no more text string after this.
                       "\n": 0xB6,  # Insert newline (without pausing).
                       " ": 0xB7}  # Insert space.
CVLOD_COMMAND_CHARS_INV = {value: key for key, value in CVLOD_COMMAND_CHARS.items()}

ARG_CHARS = {"↗", "↘", "🅰", "⏸", "⬘", "▶", "◆", "👉"}
ARG_END_CHAR = "/"

NON_ASCII_MAPPINGS = {"◊": 0x5F, "「": 0x60, "」": 0x61, "。": 0x62, "•": 0x63, "—": 0x64, "▷": 0x65, "₀": 0x66,
                      "₁": 0x67, "₂": 0x68, "₃": 0x69, "₄": 0x6A, "₅": 0x6B, "₆": 0x6C, "₇": 0x6D, "₈": 0x6E, "₉": 0x6F,
                      "〃": 0x70, "°": 0x71, "∞": 0x72, "、": 0x73}
NON_ASCII_MAPPINGS_INV = {value: key for key, value in NON_ASCII_MAPPINGS.items()}

LINE_RESET_CHARS = {"\n", "\r", "\f", "⏸", "◆"}

UNICODE_ASCII_START = 0x21
UNICODE_ASCII_END = 0x7E

LEN_LIMIT_MAP_TEXT = 254
LEN_LIMIT_MULTIWORLD_TEXT = 190

MAP_TEXT_DISPLAY_LINES = 4


def cvlod_string_to_bytearray(cvlod_text: str, len_limit: int = LEN_LIMIT_MAP_TEXT,
                              max_lines: int = 0, wrap: bool = True, textbox_a_advance: bool = False,
                              add_end_char: bool = False) -> bytearray:
    """
    Converts a string into a bytearray following Castlevania: Legacy of Darkness's text format.

    With some exceptions, most of the text character in this game are in standard ASCII order, albeit 0x20 less than
    what its ASCII encoding would be and consisting of two bytes instead of one.
    """
    # Wrap the text if we are opting to do so.
    if wrap:
        refined_text = cvlod_text_wrap(cvlod_text, len_limit, max_lines, textbox_a_advance)
    else:
        refined_text = cvlod_text

    text_bytes = bytearray(0)
    ctrl_arg_mode = False
    arg_number = "0"

    # Convert the string into CVLoD's text string format.
    for i, char in enumerate(refined_text):
        # If ctrl arg mode is on, then we should currently be iterating through a command character's argument number.
        # Handle this appropriately.
        if ctrl_arg_mode:
            # If the current character is a number digit, add it to the arg number string.
            if refined_text[i].isnumeric():
                arg_number += refined_text[i]
                continue
            # If the current character is the arg end character, and number digits were added to the arg number
            # string, convert the arg number string into a 1-byte number, add it to the text bytearray, disable ctrl
            # arg mode, and reset the arg number string.
            if refined_text[i] == ARG_END_CHAR and int(arg_number) <= 0xFF:
                text_bytes.extend(int.to_bytes(int(arg_number), 1, "big"))
                ctrl_arg_mode = False
                arg_number = "0"
                continue
            # If we made it here, then there is something off about the argument. Make the argument 00 by default,
            # throw an error explaining what went wrong, disable ctrl arg mode, and reset the arg number string.
            text_bytes.extend([0x00])
            # If the arg number is higher than 0xFF, throw an error explaining that it can't be that high.
            if int(arg_number) > 0xFF:
                logging.error(f"{arg_number} is too high to be a CVLoD control character argument. "
                              f"It needs to be 255 or less.")
            # Otherwise, throw an error explaining that the argument was incorrectly formatted with characters other
            # than number digits or the arg end character.
            else:
                logging.error("CVLoD control character argument is incorrectly formatted. It must be numbers "
                              "followed by a \"/\".")
            ctrl_arg_mode = False
            arg_number = "0"
            continue


        # If the current character is a command character, append that character's mapping in the command characters'
        # dict.
        if char in CVLOD_COMMAND_CHARS:
            text_bytes.extend([CVLOD_COMMAND_CHARS[char]])
            # If it's a command character followed by an argument, turn on ctrl arg mode for the next few loops.
            if char in ARG_CHARS:
                ctrl_arg_mode = True
            # Otherwise, consider the control arg byte 00.
            else:
                text_bytes.extend([0x00])
            continue

        # If the current character has a mapping in the non-ASCII characters dict, append that character's mapping said
        # dict.
        if char in NON_ASCII_MAPPINGS:
            text_bytes.extend(int.to_bytes(NON_ASCII_MAPPINGS[char], 2, "big"))
            continue

        # If the character didn't have a mapping in either dict, check to see if it's within the game's ASCII mappings
        # range. If it is, subtract the ASCII difference to get the actual byte the game recognizes for that character.
        if UNICODE_ASCII_START <= ord(char) <= UNICODE_ASCII_END:
            # NOTE: The ASCII space actually has its own control character in this game, which is already accounted for
            # by the control characters check.
            text_bytes.extend(int.to_bytes(ord(char) - CVLOD_ASCII_DIFFERENCE, 2, "big"))
            continue

        # If we make it all the way here, meaning it didn't get caught by any of the above checks, consider it an
        # unsupported character that we will replace with the default character.
        text_bytes.extend(int.to_bytes(ord(CVLOD_DEFAULT_CHAR) - CVLOD_ASCII_DIFFERENCE, 2, "big"))

    # Return the final in-game bytes string with or without the end character depending on whether we opted to add it.
    if add_end_char:
        text_bytes.extend(CVLOD_STRING_END_CHARACTER)
    return text_bytes


def cvlod_strings_to_pool(cvlod_texts: [str], len_limit: int = LEN_LIMIT_MAP_TEXT,
                          max_lines: int = 0, wrap: bool = True, textbox_a_advance: bool = False) -> bytearray:
    """
    Converts a list of strings into an entire text pool bytearray following Castlevania: Legacy of Darkness's text format.

    Supports wrapping each line in the same way as the single string function.
    """
    text_pool_bytes = bytearray(0)
    for pool_text in cvlod_texts:
        text_pool_bytes += (cvlod_string_to_bytearray(pool_text, len_limit=len_limit, max_lines=max_lines, wrap=wrap,
                                                      textbox_a_advance=textbox_a_advance, add_end_char=True))

    # Add the character indicating the end of the entire text pool.
    text_pool_bytes += CVLOD_TEXT_POOL_END_CHARACTER

    # Pad the text data to be 4-aligned.
    if len(text_pool_bytes) % 4:
        text_pool_bytes += b'\x00\x00'

    # Return the final result
    return text_pool_bytes


def cvlod_bytes_to_string(cvlod_str_bytes: bytes) -> str:
    """Converts a given bytes sequence following CVLoD's string format (probably one extracted from the game itself)
    into a usable Python string."""
    converted_str = ""

    for char_start in range(0, len(cvlod_str_bytes), 2):
        # Check the remaining string length to see if there are at least two bytes ahead. If there's not, meaning
        # there's only one, then throw an error and break the loop; the input string bytes should REALLY be an even
        # length!
        if len(cvlod_str_bytes[char_start:]) % 2:
            logging.error(f"The following CVLoD string bytes are of an odd length when they should be even: "
                          f"{cvlod_str_bytes}")
            break

        char_bytes = cvlod_str_bytes[char_start: char_start + 2]

        # Check if the upper byte is a command character. If it is, get the Python string character that we are using
        # for that command character.
        if char_bytes[0] in CVLOD_COMMAND_CHARS_INV:
            command_char = CVLOD_COMMAND_CHARS_INV[char_bytes[0]]

            # If the command character has an argument, add the lower byte number followed by the arg end character.
            if command_char in ARG_CHARS:
                command_char += f"{char_bytes[1]}{ARG_END_CHAR}"

            converted_str += command_char
            continue

        # If the upper byte is 0, then it's not a command character. In which case, see if we can determine which
        # standard character it is.
        if not char_bytes[0]:
            # If the lower byte is a non-ASCII character, take that mapping.
            if char_bytes[1] in NON_ASCII_MAPPINGS_INV:
                converted_str += NON_ASCII_MAPPINGS_INV[char_bytes[1]]
                continue

            # If the lower byte is in the game's ASCII range, add the game's ASCII difference to get the actual ASCII
            # encoding for that character.
            if UNICODE_ASCII_START <= char_bytes[1] + CVLOD_ASCII_DIFFERENCE <= UNICODE_ASCII_END:
                converted_str += chr(char_bytes[1] + CVLOD_ASCII_DIFFERENCE)
                continue

        # If the character is the end character, return early because we've reached the end of the string.
        if char_bytes == CVLOD_STRING_END_CHARACTER:
            return converted_str

        # If we made it all the way here, then we could not figure out what character it was supposed to be at all.
        # In which case, use the default character.
        converted_str += CVLOD_DEFAULT_CHAR

    # Return the final Python string.
    return converted_str


def cvlod_text_wrap(cvlod_text: str, textbox_len_limit: int = LEN_LIMIT_MAP_TEXT, max_lines: int = 0,
                    textbox_a_advance: bool = False) -> str:
    """Rebuilds a string with some of its spaces replaced with newlines to ensure the text wraps properly in an in-game
    textbox of a given length."""
    num_lines = 1
    new_text = []
    current_line_len = 0
    current_word_len = 0
    last_space_index = -1
    prev_character = ""
    ctrl_arg_mode = False

    for i in range(len(cvlod_text)):
        # Reset the newline insertion index to -1 to indicate no newline placement was decided for this loop (yet).
        newline_insertion_index = -1

        # If we are in ctrl param mode, add the character and continue to the next loop.
        if ctrl_arg_mode:
            new_text += cvlod_text[i]
            # If the character is the param end character, turn off ctrl param mode for the subsequent loops because
            # we've reached the end of the parameter.
            if cvlod_text[i] == ARG_END_CHAR:
                ctrl_arg_mode = False
            continue

        # Determine how much width to increase the word and line length counters by. If the character has a mapping in
        # the widths dict, use its defined width from that.
        if cvlod_text[i] in CVLOD_CHAR_WIDTHS:
            width_to_add = CVLOD_CHAR_WIDTHS[cvlod_text[i]]
        # If it's not in the widths dict, then check to see if it's in the command characters' dict. If it isn't,
        # it's an unknown character we will substitute with the default character with its default width.
        elif cvlod_text[i] not in CVLOD_COMMAND_CHARS:
            width_to_add = CVLOD_CHAR_WIDTHS[CVLOD_DEFAULT_CHAR]
        # If it was, however, then it's a special command character with no width at all. Neither the current line nor
        # word length counters should increase on this loop.
        else:
            width_to_add = 0
            # Check to see if it's one of the command characters followed by an arg. If it is, turn on ctrl arg mode
            # for the next few loops until we have made it past the param.
            if cvlod_text[i] in ARG_CHARS:
                ctrl_arg_mode = True

        # If the character we are adding is a space that would put us over the line limit, and the previously-placed
        # character was also a space, don't change anything on this loop and continue to the next one.
        if cvlod_text[i] == " " and current_line_len + width_to_add > textbox_len_limit and prev_character == " ":
            continue
        # Otherwise, add the character to the output now and record that character for the next loop.
        new_text += cvlod_text[i]
        prev_character = cvlod_text[i]

        # Add the width we selected to the current line length.
        current_line_len += width_to_add
        # If the character is not a space, add the width to the current word length as well.
        if cvlod_text[i] != " ":
            current_word_len += width_to_add
        # Otherwise, if the character is a space, record its position in the output for later and reset the current word
        # length to 0.
        else:
            last_space_index = i + (len(new_text) - 1 - i)
            current_word_len = 0

        # If the character we placed is a manually-placeable newline character, record its insertion index now and set
        # the current word and line lengths to the chosen width.
        if cvlod_text[i] in LINE_RESET_CHARS:
            newline_insertion_index = len(new_text) - 1
            current_word_len = width_to_add
            current_line_len = width_to_add

        # If we're not looking at a manually-inserted newline character and adding the width from the character did not
        # put us over the line length limit, continue to the next loop.
        if current_line_len <= textbox_len_limit and newline_insertion_index < 0:
            continue

        # If a newline character wasn't manually inserted, decide where it should be auto-inserted here.
        if newline_insertion_index < 0:
            # If a space character was recorded for this line, choose that space to place the newline over and set the
            # current line length to the current word length.
            if last_space_index >= 0:
                newline_insertion_index = last_space_index
                current_line_len = current_word_len
            # Otherwise, choose the end of the output string-list to insert the newline at, insert a dummy character
            # right before the recently-placed plain character, and set the current word and line lengths to the chosen
            # width.
            else:
                newline_insertion_index = len(new_text) - 1
                new_text.insert(len(new_text) - 1, "")
                current_word_len = width_to_add
                current_line_len = width_to_add

        # Increase the line counter, reset the last space index to -1, and choose the regular newline character to
        # insert by default.
        num_lines += 1
        last_space_index = -1
        newline_char = "\n"

        # If the current character is a line reset character, use that character as the newline character instead.
        if cvlod_text[i] in LINE_RESET_CHARS:
            newline_char = cvlod_text[i]

        # If this wrap puts us over the line limit and there is a line limit greater than Unlimited (indicated by it
        # being 0 or negative), or a clear text character was manually placed, handle the situation here.
        if (max_lines and num_lines > max_lines) or cvlod_text[i] == "\f":
            # If we opted to auto "A" advance textboxes upon hitting the max lines or manually placed a clear textbox
            # character, reset the line count back to 1 and choose the next textbox character(s) to insert instead.
            if textbox_a_advance or cvlod_text[i] == "\f":
                # If the previous character was not the A advance character AND the current character is not the clear
                # textbox character, place the A advance character followed by the clear textbox character. Otherwise,
                # place only the next textbox character.
                if prev_character != "🅰" and cvlod_text[i] != "\f":
                    newline_char = "🅰0/\f"
                else:
                    newline_char = "\f"
                num_lines = 1
            # Otherwise, if we did not opt to auto "A" advance textboxes (and as such are confined to just that one),
            # return the final joined string now.
            else:
                return "".join(new_text)

        # Place the chosen newline character at the chosen index.
        new_text[newline_insertion_index] = newline_char

    # Return the final joined, wrapped string.
    return "".join(new_text)


def cvlod_command_scrubber(cvlod_text: str) -> str:
    """Scrubs all command characters from a given text string, replacing them with the default text character.
    Good for any Archipelago player/item names that might try to be sneaky here..."""
    new_text = ""

    for char in cvlod_text:
        if char in CVLOD_COMMAND_CHARS:
            new_text += CVLOD_DEFAULT_CHAR
        else:
            new_text += char

    return new_text
