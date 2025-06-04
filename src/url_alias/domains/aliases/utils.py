BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

LCG_MULTIPLIER = 6364136223846793005
LCG_INCREMENT = 1442695040888963407
LCG_MODULUS = 2**63
LCG_INVERSE = 4654452103859546277


def encode_base62(number: int) -> str:
    if number < 0:
        raise ValueError("Input 'number' must be a non-negative integer.")
    if number == 0:
        return BASE62_ALPHABET[0]

    base62_chars = []
    base = len(BASE62_ALPHABET)

    while number > 0:
        number, remainder = divmod(number, base)
        base62_chars.append(BASE62_ALPHABET[remainder])

    return "".join(reversed(base62_chars))


def decode_base62(base62_string: str) -> int:
    if not base62_string:
        return 0

    base = len(BASE62_ALPHABET)
    result = 0

    for char in base62_string:
        if char not in BASE62_ALPHABET:
            raise ValueError(f"Invalid character '{char}' in base62 string")
        result = result * base + BASE62_ALPHABET.index(char)

    return result


def generate_short_code_from_id(alias_id: int) -> str:
    if alias_id < 0:
        raise ValueError("alias_id must be non-negative")

    scrambled = (LCG_MULTIPLIER * alias_id + LCG_INCREMENT) % LCG_MODULUS
    return encode_base62(scrambled)


def decode_short_code_to_id(short_code: str) -> int:
    scrambled = decode_base62(short_code)
    original_id = (LCG_INVERSE * (scrambled - LCG_INCREMENT)) % LCG_MODULUS
    return original_id
