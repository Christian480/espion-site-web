def encrypt_message(message, key=3):
    result = ""

    for char in message:
        if "a" <= char <= "z":
            start = ord("a")
            new_char = chr((ord(char) - start + key) % 26 + start)
            result += new_char
        elif "A" <= char <= "Z":
            start = ord("A")
            new_char = chr((ord(char) - start + key) % 26 + start)
            result += new_char
        else:
            result += char

    return result


def decrypt_message(message, key=3):
    return encrypt_message(message, -key)