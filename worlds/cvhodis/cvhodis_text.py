import logging
import struct

CVHODIS_VAR_WIDTH_CHARS = {" ": (0x40, 4, 4), ",": (0x41, 4, 4), ".": (0x42, 4, 4), "•": (0x43, 5, 4),
                           ":": (0x44, 4, 4), ";": (0x45, 4, 4), "!": (0x46, 4, 3), "I": (0x47, 4, 3),
                           "a": (0x48, 6, 5), "b": (0x49, 6, 5), "c": (0x4A, 6, 5), "d": (0x4B, 6, 5),
                           "e": (0x4C, 6, 5), "f": (0x4D, 6, 4), "g": (0x4E, 6, 6), "h": (0x4F, 6, 5),
                           "i": (0x50, 2, 2), "j": (0x51, 6, 5), "k": (0x52, 6, 5), "l": (0x53, 3, 3),
                           "m": (0x54, 6, 6), "n": (0x55, 6, 5), "o": (0x56, 6, 5), "p": (0x57, 6, 5),
                           "q": (0x58, 6, 5), "r": (0x59, 5, 5), "s": (0x5A, 6, 5), "t": (0x5B, 5, 4),
                           "u": (0x5C, 6, 5), "v": (0x5D, 6, 6), "w": (0x5E, 6, 6), "x": (0x5F, 6, 6),
                           "y": (0x60, 6, 5), "z": (0x61, 6, 5), "'": (0x62, 4, 3), "(": (0x63, 4, 3),
                           ")": (0x64, 4, 3), "$": (0x65, 6, 6)}
CVHODIS_VAR_WIDTH_CHARS_INV = {value[0]: key for key, value in CVHODIS_VAR_WIDTH_CHARS.items()}
# [0] = CVHoD's in-game ID for the variable width version of that text character.
# [1] = The width (in pixels) of the character in the large font (dialogue boxes, menu descriptions, etc.).
# [2] = The width (in pixels) of the character in the small font (item/enemy name corner textboxes, menu names, etc.).

CVHODIS_DEFAULT_CHAR = "?"
CVHODIS_DEFAULT_CHAR_BYTES = b"\x48\x81"
CVHODIS_DEFAULT_CHAR_WIDTH = 6  # For both the large and small fonts.
CVHODIS_WIDTH_CHAR_BYTE = 0x85
CVHODIS_HIGHEST_SHIFT_JIS_CHAR = 0x84BE
CVHODIS_STRING_END_CHARACTER = b"\x0A\xF0"

CVHODIS_COMMAND_CHARS = {"\b": 0x01,  # Insert a separate string here. Arg = ID of string to insert. WARNING: The text
                                      # wrap stuff here does NOT account for strings inserted using this!
                         "▶":  0x02,  # Play cutscene-specific action. Arg = what to play (1 = next action).
                         "❖":  0x03,  # Open a textbox. Arg = ID of portrait to insert on the left side.
                         "\f": 0x04,  # Close the current textbox.
                         "🅰":  0x05,  # Make the player press A to advance past here.
                         "\n": 0x06,  # Insert newline.
                         "⬘":  0x07,  # Add name string at the top of the textbox. Arg = ID of string to add.
                         "✨":  0x08,  # Change text color. Arg = Index in the BGP F palette to change the color to.
                         "\r": 0x09,  # Clear the current textbox and start drawing the next set of characters.
                         "\t": 0x0A}  # Terminate the entire string.
CVHODIS_COMMAND_CHARS_INV = {value: key for key, value in CVHODIS_COMMAND_CHARS.items()}

ARG_CHARS = {"\b", "▶", "❖", "⬘", "✨"}
ARG_END_CHAR = "/"
# Example of a control character that changes the text color to yellow: "✨4/"

# Half-width to ｆｕｌｌ－ｗｉｄｔｈ Katakana mappings as well as a few other weird UTF-8 characters likely to be used that
# don't cleanly encode to double-byte Shift-JIS (including a few even after converting to ｆｕｌｌ－ｗｉｄｔｈ Latin in some
# cases) but have a different equivalent UTF-8 char that does, in fact, encode to double-byte Shift-JIS. These
# problematic characters are listed at:
# https://www.ibm.com/docs/en/cognos-analytics/11.1.0?topic=guide-japanese-shift-jis-character-mapping
OTHER_SHIFT_JIS_ENCODINGS = {
    "－": "−", "～": "〜", "‾": "￣", "—": "—", "∥": "‖", "¢": "￠", "£": "￡", "¥": "￥", "¬": "￢", "｡": "。", "｢": "「",
    "｣": "」", "､": "、", "･": "・", "ｦ": "ヲ", "ｧ": "ァ", "ｨ": "ィ", "ｩ": "ゥ", "ｪ": "ェ", "ｫ": "ォ", "ｬ": "ャ", "ュ": "ユ",
    "ｮ": "ョ", "ｯ": "ッ", "ｰ": "ー", "ｱ": "ア", "ｲ": "イ", "ｳ": "ウ", "ｴ": "エ", "ｵ": "オ", "ｶ": "カ", "ｷ": "キ", "ｸ": "ク",
    "ｹ": "ケ", "ｺ": "コ", "ｻ": "サ", "ｼ": "シ", "ｽ": "ス", "ｾ": "セ", "ｿ": "ソ", "ﾀ": "タ", "ﾁ": "チ", "ﾂ": "ツ", "ﾃ": "テ",
    "ﾄ": "ト", "ﾅ": "ナ", "ﾆ": "ニ", "ﾇ": "ヌ", "ﾈ": "ネ", "ﾉ": "ノ", "ﾊ": "ハ", "ﾋ": "ヒ", "ﾌ": "フ", "ﾍ": "ヘ", "ﾎ": "ホ",
    "ﾏ": "マ", "ﾐ": "ミ", "ﾑ": "ム", "ﾒ": "メ", "ﾓ": "モ", "ﾔ": "ヤ", "ﾕ": "ユ", "ﾖ": "ヨ", "ﾗ": "ラ", "ﾘ": "リ", "ﾙ": "ル",
    "ﾚ": "レ", "ﾛ": "ロ", "ﾜ": "ワ", "ﾝ": "ン", "ﾞ": "゛", "ﾟ": "゜"}
OTHER_SHIFT_JIS_ENCODINGS_INV = {value: key for key, value in OTHER_SHIFT_JIS_ENCODINGS.items()}

LINE_RESET_CHARS = {"\n", "\r", "\f"}

CVHODIS_COMMAND_CHAR_BYTE = 0xF0

UNICODE_ASCII_START = 0x21
UNICODE_ASCII_END = 0x7E
UNICODE_ASCII_FULL_AND_HALF_DIFFERENCE = 0xFEE0

# Large font length limits
LEN_LIMIT_EVENT = 240
LEN_LIMIT_DIALOGUE = 168
LEN_LIMIT_MENU_DESCRIPTION = 206
# Small font length limits
LEN_LIMIT_MENU_NAME = 80
LEN_LIMIT_CORNER_TEXTBOX_ORIG = 140
LEN_LIMIT_CORNER_TEXTBOX_CUSTOM = 208

DIALOGUE_DISPLAY_LINES = 3
DESCRIPTION_DISPLAY_LINES = 2

def cvhodis_string_to_bytearray(cvhodis_text: str, large_font: bool = True, len_limit: int = LEN_LIMIT_DIALOGUE,
                                max_lines: int = DIALOGUE_DISPLAY_LINES, wrap: bool = False,
                                textbox_advance: bool = False, add_start_zeros = True,
                                add_end_char: bool = True) -> bytearray:
    """
    Converts a string into a bytearray following Castlevania: Harmony of Dissonance's text format.

    The game's strings are encoded in Shift JIS (more specifically, the double-byte ｆｕｌｌ－ｗｉｄｔｈ character variants;
    single-byte half-width characters are NOT supported by the game at all) with some notable weirdness in how
    characters with widths other than 6 pixels are handled.

    All double-byte ｆｕｌｌ－ｗｉｄｔｈ characters up to and including 0x84BE ("╂") seem to be supported. To get
    characters properly spaced like how the game normally does, however, we need to use their unique game-specific
    equivalent encoding in the 0x85xx byte range instead of what they'd otherwise be in standard Shift JIS. Standard
    Shift JIS encodings do exist in-game for every character, but those variants all use the max width of 6 pixels
    across. Command characters all exist in the 0xF0xx range. Single-byte half-width characters are NOT supported by the
    game at all, so any half-width Katakana and Latin characters MUST be converted to ｆｕｌｌ－ｗｉｄｔｈ to then encode
    properly (if they don't already have a variable width character in-game that we can just convert directly to).

    I spent way too long going down the rabbit hole of Japanese character encodings just to be able to write all this,
    if you haven't been able to tell already...
    """
    # Wrap the text if we are opting to do so.
    if wrap:
        refined_text = cvhodis_text_wrap(cvhodis_text, large_font, len_limit, max_lines, textbox_advance)
    else:
        refined_text = cvhodis_text

    text_bytes = bytearray(0)
    ctrl_arg_mode = False
    arg_number = "0"

    # Add the start 0000 bytes if we are opting to do so.
    if add_start_zeros:
        text_bytes.extend([0x00, 0x00])

    # Convert the string into CVHoD's text string format.
    for i, char in enumerate(refined_text):
        # If ctrl arg mode is on, then we should currently be iterating through a command character's argument number.
        # Handle things appropriately.
        if ctrl_arg_mode:
            # If the current character is a number digit, add it to the arg number string.
            if refined_text[i].isnumeric():
                arg_number += refined_text[i]
                continue
            # If the current character is the arg end character, and number digits were added to the arg number
            # string, convert the arg number string into a 2-byte number, add it to the text bytearray, disable ctrl
            # arg mode, and reset the arg number string.
            if refined_text[i] == ARG_END_CHAR and int(arg_number) <= 0xFFFF:
                text_bytes.extend(int.to_bytes(int(arg_number), 2, "little"))
                ctrl_arg_mode = False
                arg_number = "0"
                continue
            # If we made it here, then there is something off about the argument. Make the argument 0000 by default,
            # throw an error explaining what went wrong, disable ctrl arg mode, and reset the arg number string.
            text_bytes.extend([0x00, 0x00])
            # If the arg number is higher than 0xFFFF, throw an error explaining that it can't be that high.
            if int(arg_number) > 0xFFFF:
                logging.error(f"{arg_number} is too high to be a CVHoDis control character argument. "
                              f"It needs to be 65535 or less.")
            # Otherwise, throw an error explaining that the argument was incorrectly formatted with characters other
            # than number digits or the arg end character.
            else:
                logging.error('CVHoDis control character argument is incorrectly formatted. It must be numbers '
                              'followed by a "/".')
            ctrl_arg_mode = False
            arg_number = "0"
            continue


        # If the current character is a command character, append that character's mapping in the command characters
        # dict plus the byte signifying it's a command character.
        if char in CVHODIS_COMMAND_CHARS:
            text_bytes.extend([CVHODIS_COMMAND_CHARS[char], CVHODIS_COMMAND_CHAR_BYTE])
            # If it's a command character followed by a argument, turn on ctrl arg mode for the next few loops.
            if char in ARG_CHARS:
                ctrl_arg_mode = True
            continue

        # If the current character is a variable width character, append that character's mapping in the variable width
        # characters plus the byte signifying it's a variable width character.
        if char in CVHODIS_VAR_WIDTH_CHARS:
            text_bytes.extend([CVHODIS_VAR_WIDTH_CHARS[char][0], CVHODIS_WIDTH_CHAR_BYTE])
            continue

        # If the character didn't have a mapping in either dict, append its standard Shift JIS double byte encoding.
        # Check if the character's UTF-8 encoding is in the correct range to be standard ASCII half-width Latin. If it
        # is, convert it to ｆｕｌｌ－ｗｉｄｔｈ. If it isn't assume it's already ｆｕｌｌ－ｗｉｄｔｈ.
        char_to_encode = char
        if UNICODE_ASCII_START <= ord(char) <= UNICODE_ASCII_END:
            # NOTE: This adding method doesn't work for the ASCII space specifically, but it doesn't matter because the
            # space should be caught and handled by the variable width characters' handling.
            char_to_encode = chr(UNICODE_ASCII_FULL_AND_HALF_DIFFERENCE + ord(char))

        # Check to see if the character has a mapping in the other Shift-JIS encodings dict. If it does, use the
        # different character mapped to it there instead so it'll actually encode to double-byte Shift-JIS properly.
        if char_to_encode in OTHER_SHIFT_JIS_ENCODINGS:
            char_to_encode = OTHER_SHIFT_JIS_ENCODINGS[char_to_encode]
        # Try encoding the character in Shift-JIS.
        try:
            jis_char = char_to_encode.encode("Shift-JIS")
            # If the character encodes to something higher than the game supports, or if it's a single-byte character
            # that didn't get caught in any of the above checks, then consider it an unsupported character that we will
            # replace with the default character. Otherwise, go ahead and append it.
            if 0xFF >= int.from_bytes(jis_char, "big") > CVHODIS_HIGHEST_SHIFT_JIS_CHAR:
                text_bytes.extend(CVHODIS_DEFAULT_CHAR_BYTES)
            else:
                text_bytes.extend([jis_char[1], jis_char[0]])
        # If it didn't encode at all, then it's (probably) an unsupported character that we will replace with the
        # default character.
        except UnicodeEncodeError:
            text_bytes.extend(CVHODIS_DEFAULT_CHAR_BYTES)

    # Return the final in-game bytes string with or without the end character depending on whether we opted to add it,
    # plus an additional 0000 to be accurate to the game.
    if add_end_char:
        text_bytes.extend(CVHODIS_STRING_END_CHARACTER + b'\x00\x00')
        # Pad the text data to be 4-aligned.
        if len(text_bytes) % 4:
            text_bytes += b'\x00\x00'

    return text_bytes


def cvhodis_bytes_to_string(cvhodis_str_bytes: bytes) -> str:
    """Converts a given bytes sequence following HoD's string format (probably one extracted from the game itself)
    into a UTF-8 string Python can use."""
    converted_str = ""
    ctrl_arg_mode = False

    for char_start in range(0, len(cvhodis_str_bytes), 2):
        # Check the remaining string length to see if there are at least two bytes ahead. If there's not, meaning
        # there's only one, then throw an error and break the loop; the input string bytes should REALLY be an even
        # length!
        if len(cvhodis_str_bytes[char_start:]) % 2:
            logging.error(f"The following CVHoDis string bytes are of an odd length when they should be even: "
                          f"{cvhodis_str_bytes}")
            break

        char_bytes = cvhodis_str_bytes[char_start: char_start + 2]

        # If the character is 0000, and we are not in ctrl arg mode, skip processing it.
        # This is almost certainly the start-of-string character.
        if char_bytes == b'\00\00' and not ctrl_arg_mode:
            continue

        # If ctrl arg mode is on, then we are currently looking at the argument number value for a command character.
        # In which case, add the arg number followed by the arg end character.
        if ctrl_arg_mode:
            converted_str += f"{struct.unpack('<H', char_bytes)[0]}{ARG_END_CHAR}"
            # Turn off ctrl arg mode so we will go back to checking for regular characters on the next iteration.
            ctrl_arg_mode = False
            continue

        # If the character is the end character, return early because we've reached the end of the string.
        if char_bytes == CVHODIS_STRING_END_CHARACTER:
            return converted_str

        # Check if the lower byte is the command character byte and that the upper byte is in the command chars dict.
        # If both are true, get the Python string character that we are using for that command character.
        if char_bytes[0] in CVHODIS_COMMAND_CHARS_INV and char_bytes[1] == CVHODIS_COMMAND_CHAR_BYTE:
            command_char = CVHODIS_COMMAND_CHARS_INV[char_bytes[0]]

            # If the command character has an argument, turn on ctrl arg mode for the next iteration.
            if command_char in ARG_CHARS:
                ctrl_arg_mode = True

            converted_str += command_char
            continue

        # If we made it all the way here, then it's not a command character.
        # In which case, see if we can determine which standard character it is.

        # If the high byte is the value indicating it's a variable width character, see if it has a mapping in the
        # inverted variable width characters dict. And if it does, take that mapping.
        if char_bytes[1] == CVHODIS_WIDTH_CHAR_BYTE:
            if char_bytes[0] in CVHODIS_VAR_WIDTH_CHARS_INV:
                converted_str += CVHODIS_VAR_WIDTH_CHARS_INV[char_bytes[0]]
            # If it did not have a mapping in the inverted variable widths dict, use the default character.
            else:
                converted_str += CVHODIS_DEFAULT_CHAR
            continue

        # If the high byte was NOT the variable width value, then try decoding it as a regular Shift-JIS character.
        try:
            decoded_char = char_bytes[::-1].decode("Shift-JIS")
            # Get the character's half-width form, because we decoded from double-byte Shift-JIS.
            # If it's in the inverted dictionary of misc. non-ASCII full width characters, use the mapping from that.
            if decoded_char in OTHER_SHIFT_JIS_ENCODINGS_INV:
                converted_str += OTHER_SHIFT_JIS_ENCODINGS_INV[decoded_char]
            # If not, check if it's ASCII full width. If it is, subtract the Unicode full and half width ASCII
            # difference from the chracter's ord value to get the ASCII half width version and append that.
            elif UNICODE_ASCII_START <= ord(decoded_char) - UNICODE_ASCII_FULL_AND_HALF_DIFFERENCE <= UNICODE_ASCII_END:
                converted_str += chr(ord(decoded_char) - UNICODE_ASCII_FULL_AND_HALF_DIFFERENCE)
            # Otherwise, meaning it wasn't an ASCII full width character, append the character as-is.
            else:
                converted_str += decoded_char

        # If it failed to decode, consider it a completely unknown character that we will use the default character for.
        except UnicodeDecodeError:
            converted_str += CVHODIS_DEFAULT_CHAR

    # Return the final UTF-8 string.
    return converted_str


def cvhodis_text_wrap(cvhodis_text: str, large_font: bool, textbox_len_limit: int, max_lines: int,
                      textbox_advance: bool) -> str:
    """Rebuilds a string with some of its spaces replaced with newlines to ensure the text wraps properly in an in-game
    textbox of a given length."""
    num_lines = 1
    new_text = []
    current_line_len = 0
    current_word_len = 0
    last_space_index = -1
    prev_character = ""
    ctrl_arg_mode = False

    for i in range(len(cvhodis_text)):
        # Reset the newline insertion index to -1 to indicate no newline placement was decided for this loop (yet).
        newline_insertion_index = -1

        # If we are in ctrl arg mode, add the character and continue to the next loop.
        if ctrl_arg_mode:
            new_text += cvhodis_text[i]
            # If the character is the arg end character, turn off ctrl arg mode for the subsequent loops because
            # we've reached the end of the argument.
            if cvhodis_text[i] == ARG_END_CHAR:
                ctrl_arg_mode = False
            continue

        # Determine how much width to increase the word and line length counters by. If the character is in the variable
        # widths dict, use its defined width from that.
        if cvhodis_text[i] in CVHODIS_VAR_WIDTH_CHARS:
            # If we're dealing with the large font, use the large font width.
            if large_font:
                width_to_add = CVHODIS_VAR_WIDTH_CHARS[cvhodis_text[i]][1]
            # Otherwise, meaning we're dealing with the small font, use the small font width.
            else:
                width_to_add = CVHODIS_VAR_WIDTH_CHARS[cvhodis_text[i]][2]
        # If it's not in the variable widths dict, then check to see if it's in the command characters' dict. If it
        # isn't, it's a standard character with the default width. The default char width is the same for both fonts.
        elif cvhodis_text[i] not in CVHODIS_COMMAND_CHARS:
            width_to_add = CVHODIS_DEFAULT_CHAR_WIDTH
        # If it was, however, then it's a special command character with no width at all. Neither the current line nor
        # word length counters should increase on this loop.
        else:
            width_to_add = 0
            # Check to see if it's one of the command characters followed by a arg. If it is, turn on ctrl arg mode
            # for the next few loops until we have made it past the arg.
            if cvhodis_text[i] in ARG_CHARS:
                ctrl_arg_mode = True

        # If the character we are adding is a space that would put us over the line limit, and the previously-placed
        # character was also a space, don't change anything on this loop and continue to the next one.
        if cvhodis_text[i] == " " and current_line_len + width_to_add > textbox_len_limit and prev_character == " ":
            continue
        # Otherwise, add the character to the output now and record that character for the next loop.
        new_text += cvhodis_text[i]
        prev_character = cvhodis_text[i]

        # Add the width we selected to the current line length.
        current_line_len += width_to_add
        # If the character is not a space, add the width to the current word length as well.
        if cvhodis_text[i] != " ":
            current_word_len += width_to_add
        # Otherwise, if the character is a space, record its position in the output for later and reset the current word
        # length to 0.
        else:
            last_space_index = i + (len(new_text) - 1 - i)
            current_word_len = 0

        # If the character we placed is a manually-placeable newline character, record its insertion index now and set
        # the current word and line lengths to the chosen width.
        if cvhodis_text[i] in LINE_RESET_CHARS:
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

        # If this wrap puts us over the line limit and there is a line limit greater than Unlimited (indicated by it
        # being 0 or negative), or a next textbox character was manually placed, handle the situation here.
        if (max_lines and num_lines > max_lines) or cvhodis_text[i] in ["\r", "\f"]:
            # If we opted to auto-advance textboxes upon hitting the max lines or manually placed a next textbox
            # character, reset the line count back to 1 and choose the next textbox character(s) to insert instead.
            if textbox_advance or cvhodis_text[i] in ["\r", "\f"]:
                # If the previous character was not the A advance character AND the current character is not the next
                # textbox character, place the A advance character along with the next textbox character. Otherwise,
                # place only the next textbox character.
                if cvhodis_text[i] not in ["\r", "\f"]:
                    newline_char = "🅰\r"
                # If the current character was the close textbox character, place that one instead of the next textbox
                # one.
                elif cvhodis_text[i] == "\f":
                    newline_char = "\f"
                else:
                    newline_char = "\r"
                num_lines = 1
            # Otherwise, if we did not opt to auto-advance textboxes (and as such are confined to just that one), return
            # the final joined string now, with the plain character we just added replaced with the terminate character,
            # truncating it here.
            else:
                new_text[len(new_text) - 1] = "\t"
                return "".join(new_text)

        # Place the chosen newline character at the chosen index.
        new_text[newline_insertion_index] = newline_char

    # Return the final joined, wrapped string.
    return "".join(new_text)
