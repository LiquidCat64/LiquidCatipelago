
"""
Compression and Decompression Utility for Konami's proprietary N64 compression format, known as LZKN64 aka Nagano.

The original repo used to be at https://github.com/Fluvian/lzkn64 before Fluvian deleted his entire online presence,
tho not before licensing it under MIT and giving permission to convert it from C to Python.

This LZKN64's compress_buffer differs slightly from those of other Python ones you may find elsewhere, for practicality
reasons. The Numba and Numpy imports and uses have been removed (so it's not necessary for Archipelago add those to its
dependencies), the sliding window search code has been optimized drastically better for Python bytearrays, and the code
made to intentionally recreate a bug with the forward RLE window being limited in the vanilla compressed files (for
matching purposes) has been removed for being both slow and unnecessary for this project's purposes.
"""

TYPE_COMPRESS = 1
TYPE_DECOMPRESS = 2

MODE_NONE = 0x7F
MODE_WINDOW_COPY = 0x00
MODE_RAW_COPY = 0x80
MODE_RLE_WRITE_A = 0xC0
MODE_RLE_WRITE_B = 0xE0
MODE_RLE_WRITE_C = 0xFF

WINDOW_SIZE = 0x3DF
COPY_SIZE = 0x21
RLE_SIZE = 0x101


# Compresses the data in the buffer specified in the arguments.
def compress_buffer(input_buffer: bytearray) -> bytearray:
    # Position of the current read location in the buffer.
    buffer_position = 0

    # Compressed buffer to return after the compression finishes.
    output_buffer = bytearray(4)

    # Position in the input buffer of the last time one of the copy modes was used.
    buffer_last_copy_position = 0

    while buffer_position < len(input_buffer):
        # Calculate maximum length we are able to copy without going out of bounds.
        if COPY_SIZE <= len(input_buffer) - buffer_position:
            sliding_window_maximum_length = COPY_SIZE
        else:
            sliding_window_maximum_length = len(input_buffer) - buffer_position

        # Calculate how far we are able to look back without going behind the start of the uncompressed buffer.
        if buffer_position - WINDOW_SIZE > 0:
            sliding_window_maximum_offset = buffer_position - WINDOW_SIZE
        else:
            sliding_window_maximum_offset = 0

        # Calculate maximum length the forwarding looking window is able to search.
        if RLE_SIZE < len(input_buffer) - buffer_position - 1:
            forward_window_maximum_length = RLE_SIZE
        else:
            forward_window_maximum_length = len(input_buffer) - buffer_position

        sliding_window_match_position = -1
        sliding_window_match_size = 0

        forward_window_match_value = 0
        forward_window_match_size = 0

        # The current mode the compression algorithm prefers. (0x7F == None)
        current_mode = MODE_NONE

        # The current submode the compression algorithm prefers.
        current_submode = MODE_NONE

        # How many bytes will have to be copied in the raw copy command.
        raw_copy_size = buffer_position - buffer_last_copy_position

        """Look backwards in the buffer, is there a sequence of bytes that match the ones starting at the current
        position? If yes, save the match size and last match position in the search buffer, and keep searching for
        progressively larger sequences of values from the current buffer position in the window until we no longer find
        a match that starts before the current position or we exceed the maximum sequence length."""
        sliding_window = input_buffer[sliding_window_maximum_offset: buffer_position + sliding_window_maximum_length]
        start_limit = len(sliding_window) - sliding_window_maximum_length
        sequence_to_find = bytearray(0)
        match_position = 0
        while sliding_window_match_size < sliding_window_maximum_length:
            sequence_to_find = input_buffer[buffer_position: buffer_position + sliding_window_match_size + 1]
            found_sequence_position = sliding_window.find(sequence_to_find)
            if found_sequence_position == -1 or found_sequence_position >= start_limit:
                break
            sliding_window_match_size += 1
            match_position = found_sequence_position

        # Search for an instance of our longest sequence that is furthest in the window.
        if sliding_window_match_size > 0:
            if sliding_window_match_size != sliding_window_maximum_length:
                sequence_to_find = sequence_to_find[:len(sequence_to_find) - 1]
            while True:
                next_right_position = sliding_window.find(sequence_to_find, match_position + 1)
                if next_right_position == -1 or next_right_position >= start_limit:
                    break
                match_position = next_right_position
            sliding_window_match_position = buffer_position - (len(sliding_window) - match_position -
                                                               sliding_window_maximum_length)

        """Look one step forward in the buffer, is there a matching value?
        If yes, search further and check for a repeating value in a loop.
        If no, continue to the rest of the function."""
        matching_sequence_value = input_buffer[buffer_position]
        matching_sequence_size = 0

        # If our matching sequence number is not 0x00, set the forward window maximum length to the copy size minus 1.
        # This is the highest it can really be in that case.
        if matching_sequence_value != 0 and forward_window_maximum_length > COPY_SIZE - 1:
            forward_window_maximum_length = COPY_SIZE - 1

        while input_buffer[buffer_position + matching_sequence_size] == matching_sequence_value:
            matching_sequence_size += 1

            # If we find a sequence of matching values, save them.
            if matching_sequence_size >= 1:
                forward_window_match_value = matching_sequence_value
                forward_window_match_size = matching_sequence_size

            if matching_sequence_size >= forward_window_maximum_length:
                break

        # Pick which mode works best with the current values.
        if sliding_window_match_size >= 4 and sliding_window_match_size > forward_window_match_size:
            current_mode = MODE_WINDOW_COPY

        elif forward_window_match_size >= 3:
            current_mode = MODE_RLE_WRITE_A

            if forward_window_match_value != 0x00:
                current_submode = MODE_RLE_WRITE_A
            elif forward_window_match_value == 0x00 and forward_window_match_size < COPY_SIZE:
                current_submode = MODE_RLE_WRITE_B
            elif forward_window_match_value == 0x00 and forward_window_match_size >= COPY_SIZE:
                current_submode = MODE_RLE_WRITE_C

        elif forward_window_match_size >= 2 and forward_window_match_value == 0x00:
            current_mode = MODE_RLE_WRITE_A
            current_submode = MODE_RLE_WRITE_B

        """Write a raw copy command when these following conditions are met:
        The current mode is set and there are raw bytes available to be copied.
        The raw byte length exceeds the maximum length that can be stored.
        Raw bytes need to be written due to the proximity to the end of the buffer."""
        if (current_mode != MODE_NONE and raw_copy_size >= 1) or raw_copy_size >= 0x1F \
                or buffer_position + 1 == len(input_buffer):
            if buffer_position + 1 == len(input_buffer):
                raw_copy_size = len(input_buffer) - buffer_last_copy_position

            while raw_copy_size > 0:
                if raw_copy_size > 0x1F:
                    output_buffer.append(MODE_RAW_COPY | 0x1F)

                    for written_bytes in range(0x1F):
                        output_buffer.append(input_buffer[buffer_last_copy_position])
                        buffer_last_copy_position += 1

                    raw_copy_size -= 0x1F
                else:
                    output_buffer.append(MODE_RAW_COPY | raw_copy_size & 0x1F)

                    for written_bytes in range(raw_copy_size):
                        output_buffer.append(input_buffer[buffer_last_copy_position])
                        buffer_last_copy_position += 1

                    raw_copy_size = 0

        if current_mode == MODE_WINDOW_COPY:
            output_buffer.append(MODE_WINDOW_COPY | ((sliding_window_match_size - 2) & 0x1F) << 2
                                 | (((buffer_position - sliding_window_match_position) & 0x300) >> 8))
            output_buffer.append((buffer_position - sliding_window_match_position) & 0xFF)

            buffer_position += sliding_window_match_size
            buffer_last_copy_position = buffer_position

        elif current_mode == MODE_RLE_WRITE_A:
            if current_submode == MODE_RLE_WRITE_A:
                output_buffer.append(MODE_RLE_WRITE_A | (forward_window_match_size - 2) & 0x1F)
                output_buffer.append(forward_window_match_value & 0xFF)

            elif current_submode == MODE_RLE_WRITE_B:
                output_buffer.append(MODE_RLE_WRITE_B | (forward_window_match_size - 2) & 0x1F)

            elif current_submode == MODE_RLE_WRITE_C:
                output_buffer.append(MODE_RLE_WRITE_C)
                output_buffer.append((forward_window_match_size - 2) & 0xFF)

            buffer_position += forward_window_match_size
            buffer_last_copy_position = buffer_position
        else:
            buffer_position += 1

    # Write the compressed size.
    output_buffer[1] = 0x00
    output_buffer[1] = len(output_buffer) >> 16 & 0xFF
    output_buffer[2] = len(output_buffer) >> 8 & 0xFF
    output_buffer[3] = len(output_buffer) & 0xFF

    if len(output_buffer) % 2 != 0:
        output_buffer.append(0x00)

    return output_buffer


# Decompresses the data in the buffer specified in the arguments.
def decompress_buffer(input_buffer: bytearray) -> bytearray:
    # Position of the current read location in the buffer.
    buffer_position = 4

    # Get the compressed size.
    compressed_size = (input_buffer[1] << 16) + (input_buffer[2] << 8) + input_buffer[3]

    # Compressed buffer to return after the compression finishes.
    output_buffer = bytearray(0)

    while buffer_position < compressed_size:
        mode_command = input_buffer[buffer_position]
        buffer_position += 1

        if MODE_WINDOW_COPY <= mode_command < MODE_RAW_COPY:
            copy_length = (mode_command >> 2) + 2
            copy_offset = input_buffer[buffer_position] + (mode_command << 8) & 0x3FF
            buffer_position += 1

            for current_length in range(copy_length, 0, -1):
                output_buffer.append(output_buffer[len(output_buffer) - copy_offset])
        elif MODE_RAW_COPY <= mode_command < MODE_RLE_WRITE_A:
            copy_length = mode_command & 0x1F

            for current_length in range(copy_length, 0, -1):
                output_buffer.append(input_buffer[buffer_position])
                buffer_position += 1
        elif MODE_RLE_WRITE_A <= mode_command <= MODE_RLE_WRITE_C:
            write_length = 0
            write_value = 0x00

            if MODE_RLE_WRITE_A <= mode_command < MODE_RLE_WRITE_B:
                write_length = (mode_command & 0x1F) + 2
                write_value = input_buffer[buffer_position]
                buffer_position += 1
            elif MODE_RLE_WRITE_B <= mode_command < MODE_RLE_WRITE_C:
                write_length = (mode_command & 0x1F) + 2
            elif mode_command == MODE_RLE_WRITE_C:
                write_length = input_buffer[buffer_position] + 2
                buffer_position += 1

            for current_length in range(write_length, 0, -1):
                output_buffer.append(write_value)

    # Return the current position of the write buffer, essentially giving us the size of the write buffer.
    while len(output_buffer) % 16 != 0:
        output_buffer.append(0x00)
    return output_buffer
