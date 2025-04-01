import logging

CVHODIS_UNIQUE_WIDTH_CHARS = {" ": (0x40, 4), ",": (0x41, 4), ".": (0x42, 4), "•": (0x43, 5), ":": (0x44, 4),
                              ";": (0x45, 4), "!": (0x46, 4), "I": (0x47, 4), "a": (0x48, 6), "b": (0x49, 6),
                              "c": (0x4A, 6), "d": (0x4B, 6), "e": (0x4C, 6), "f": (0x4D, 6), "g": (0x4E, 6),
                              "h": (0x4F, 6), "i": (0x50, 2), "j": (0x51, 6), "k": (0x52, 6), "l": (0x53, 3),
                              "m": (0x54, 6), "n": (0x55, 6), "o": (0x56, 6), "p": (0x57, 6), "q": (0x58, 6),
                              "r": (0x59, 5), "s": (0x5A, 6), "t": (0x5B, 5), "u": (0x5C, 6), "v": (0x5D, 6),
                              "w": (0x5E, 6), "x": (0x5F, 6), "y": (0x60, 6), "z": (0x61, 6), "'": (0x62, 4),
                              "(": (0x63, 4), ")": (0x64, 4), "$": (0x65, 6)}
# [0] = CVHoD's in-game ID for the unique width version of that text character.
# [1] = The width (in pixels) that the character contributes towards the line length.

CVHODIS_DEFAULT_CHAR = [0x48, 0x81]  # "?"
CVHODIS_DEFAULT_CHAR_WIDTH = 6
CVHODIS_WIDTH_CHAR_BYTE = 0x85
CVHODIS_HIGHEST_SHIFT_JIS_CHAR = 0x84BE

CVHODIS_COMMAND_CHARS = {"\b": 0x01,  # Insert a separate string here. Param = ID of string to insert. WARNING: The text
                                      # wrap stuff here does NOT account for strings inserted using this!
                         "▶":  0x02,  # Play cutscene-specific action. Param = what to play (1 = next action).
                         "❖":  0x03,  # Open a textbox. Param = ID of portrait to insert on the left side.
                         "\f": 0x04,  # Close the current textbox.
                         "🅰":  0x05,  # Make the player press A to advance past here.
                         "\n": 0x06,  # Insert newline.
                         "⬘":  0x07,  # Add name string at the top of the textbox. Param = ID of string to add.
                         "✨":  0x08,  # Change text color. Param = Index in the BGP F palette to change the color to.
                         "\r": 0x09,  # Clear the current textbox and start drawing the next set of characters.
                         "\t": 0x0A}  # Terminate the entire string.

PARAM_CHARS = {"\b", "▶", "❖", "⬘", "✨"}
PARAM_END_CHAR = "/"
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

NEWLINE_CHARS = {"\n", "\r", "\f"}

CVHODIS_COMMAND_CHAR_BYTE = 0xF0

UNICODE_ASCII_START = 0x21
UNICODE_ASCII_END = 0x7E
UNICODE_ASCII_FULL_AND_HALF_DIFFERENCE = 0xFEE0

LEN_LIMIT_EVENT = 240
LEN_LIMIT_DIALOGUE = 168
LEN_LIMIT_DESCRIPTION = 206

DIALOGUE_DISPLAY_LINES = 3
DESCRIPTION_DISPLAY_LINES = 2

def cvhodis_string_to_bytearray(cvhodis_text: str, len_limit: int = LEN_LIMIT_DIALOGUE,
                                max_lines: int = DIALOGUE_DISPLAY_LINES, wrap: bool = True,
                                textbox_advance: bool = True, add_start_zeros = True) -> bytearray:
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
    properly (if they don't already have a unique width character in-game that we can just convert directly to).

    I spent way too long going down the rabbit hole of Japanese character encodings just to be able to write all this,
    if you haven't been able to tell already...
    """
    # Wrap the text if we are opting to do so.
    if wrap:
        refined_text = cvhodis_text_wrap(cvhodis_text, len_limit, max_lines, textbox_advance)
    else:
        refined_text = cvhodis_text

    text_bytes = bytearray(0)
    ctrl_param_mode = False
    param_number = "0"

    # Add the start 0000 bytes if we are opting to do so.
    if add_start_zeros:
        text_bytes.extend([0x00, 0x00])

    # Convert the string into CVHoD's text string format.
    for i, char in enumerate(refined_text):
        # If ctrl param mode is on, then we should currently be iterating through a command character's parameter
        # enclosed in parentheses. Handle things appropriately.
        if ctrl_param_mode:
            # If the current character is a number digit, add it to the param number string.
            if refined_text[i].isnumeric():
                param_number += refined_text[i]
                continue
            # If the current character is the param end character, and number digits were added to the param number
            # string, convert the param number string into a 2-byte number, add it to the text bytearray, disable ctrl
            # param mode, and reset the param number string.
            if refined_text[i] == PARAM_END_CHAR and int(param_number) <= 0xFFFF:
                text_bytes.extend(int.to_bytes(int(param_number), 2, "little"))
                ctrl_param_mode = False
                param_number = "0"
                continue
            # If we made it here, then there is something off about the parameter. Make the parameter 0000 by default,
            # throw an error explaining what went wrong, disable ctrl param mode, and reset the param number string.
            text_bytes.extend([0x00, 0x00])
            # If the param number is higher than 0xFFFF, throw an error explaining that it can't be that high.
            if int(param_number) > 0xFFFF:
                logging.error(f"{param_number} is too high to be a CVHoDis control character parameter. "
                              f"It needs to be 65535 or less.")
            # Otherwise, throw an error explaining that the parameter was incorrectly formatted with characters other
            # than number digits or the param end character.
            else:
                logging.error("CVHoDis control character parameter is incorrectly formatted. It must be numbers "
                              "followed by a \"/\".")
            ctrl_param_mode = False
            param_number = "0"
            continue


        # If the current character is a command character, append that character's mapping in the command characters
        # dict plus the byte signifying it's a command character.
        if char in CVHODIS_COMMAND_CHARS:
            text_bytes.extend([CVHODIS_COMMAND_CHARS[char], CVHODIS_COMMAND_CHAR_BYTE])
            # If it's a command character followed by a parameter, turn on ctrl param mode for the next few loops.
            if char in PARAM_CHARS:
                ctrl_param_mode = True
            continue

        # If the current character is a unique width character, append that character's mapping in the unique width
        # characters plus the byte signifying it's a unique width character.
        if char in CVHODIS_UNIQUE_WIDTH_CHARS:
            text_bytes.extend([CVHODIS_UNIQUE_WIDTH_CHARS[char][0], CVHODIS_WIDTH_CHAR_BYTE])
            continue

        # If the character didn't have a mapping in either dict, append its standard Shift JIS double byte encoding.
        # Check if the character's UTF-8 encoding is in the correct range to be standard ASCII half-width Latin. If it
        # is, convert it to ｆｕｌｌ－ｗｉｄｔｈ. If it isn't assume it's already ｆｕｌｌ－ｗｉｄｔｈ.
        char_to_encode = char
        if UNICODE_ASCII_START <= ord(char) <= UNICODE_ASCII_END:
            # NOTE: This adding method doesn't work for the ASCII space specifically, but it doesn't matter because the
            # space is already accounted for by the unique width characters' handling.
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
                text_bytes.extend(CVHODIS_DEFAULT_CHAR)
            else:
                text_bytes.extend([jis_char[1], jis_char[0]])
        # If it didn't encode at all, then it's (probably) an unsupported character that we will replace with the
        # default character.
        except UnicodeEncodeError:
            text_bytes.extend(CVHODIS_DEFAULT_CHAR)

    return text_bytes


def cvhodis_text_wrap(cvhodis_text: str, textbox_len_limit: int, max_lines: int, textbox_advance: bool) -> str:
    """Rebuilds a string with some of its spaces replaced with newlines to ensure the text wraps properly in an in-game
    textbox of a given length."""
    num_lines = 1
    new_text = []
    current_line_len = 0
    current_word_len = 0
    last_space_index = -1
    prev_character = ""
    ctrl_param_mode = False

    for i in range(len(cvhodis_text)):
        # Reset the newline insertion index to -1 to indicate no newline placement was decided for this loop (yet).
        newline_insertion_index = -1

        # If we are in ctrl param mode, add the character and continue to the next loop.
        if ctrl_param_mode:
            new_text += cvhodis_text[i]
            # If the character is the param end character, turn off ctrl param mode for the subsequent loops because
            # we've reached the end of the parameter.
            if cvhodis_text[i] == PARAM_END_CHAR:
                ctrl_param_mode = False
            continue

        # Determine how much width to increase the word and line length counters by. If the character is in the unique
        # widths dict, use its defined width from that.
        if cvhodis_text[i] in CVHODIS_UNIQUE_WIDTH_CHARS:
            width_to_add = CVHODIS_UNIQUE_WIDTH_CHARS[cvhodis_text[i]][1]
        # If it's not in the unique widths dict, then check to see if it's in the command characters' dict. If it isn't,
        # it's a standard character with the default width.
        elif cvhodis_text[i] not in CVHODIS_COMMAND_CHARS:
            width_to_add = CVHODIS_DEFAULT_CHAR_WIDTH
        # If it was, however, then it's a special command character with no width at all. Neither the current line nor
        # word length counters should increase on this loop.
        else:
            width_to_add = 0
            # Check to see if it's one of the command characters followed by a param. If it is, turn on ctrl param mode
            # for the next few loops until we have made it past the param.
            if cvhodis_text[i] in PARAM_CHARS:
                ctrl_param_mode = True

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
        if cvhodis_text[i] in NEWLINE_CHARS:
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
