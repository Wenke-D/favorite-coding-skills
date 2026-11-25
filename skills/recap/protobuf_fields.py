"""Reads the fields of a protobuf message without its schema."""


def varint(data, pos):
    """The varint that starts at `pos`, and the position after it."""
    value = shift = 0
    while True:
        if pos >= len(data):
            raise ValueError("varint runs past the end")
        byte = data[pos]
        pos += 1
        value |= (byte & 0x7F) << shift
        shift += 7
        if byte < 0x80:
            return value, pos


def fields(data):
    """The (number, value) pairs of a message in order: an int for a varint, bytes for any other field.

    Raises ValueError when `data` is not a message.
    """
    pos, out = 0, []
    while pos < len(data):
        key, pos = varint(data, pos)
        number, wire = key >> 3, key & 7
        if wire == 0:
            value, pos = varint(data, pos)
        elif wire in (1, 5):
            size = 8 if wire == 1 else 4
            value, pos = data[pos:pos + size], pos + size
        elif wire == 2:
            size, pos = varint(data, pos)
            value, pos = data[pos:pos + size], pos + size
        else:
            raise ValueError(f"wire type {wire} is not read")
        if number == 0 or pos > len(data):
            raise ValueError("not a message")
        out.append((number, value))
    return out


def every(data, number):
    """The values of field `number` of a message, in order."""
    return [value for n, value in fields(data) if n == number]


def first(data, *path):
    """The first value at the field numbers `path`, each a message inside the one before; None when missing."""
    for number in path:
        values = every(data, number) if isinstance(data, bytes) else []
        if not values:
            return None
        data = values[0]
    return data
