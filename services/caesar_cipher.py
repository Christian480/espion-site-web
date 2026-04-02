<<<<<<< HEAD
def caesar_encode(text, shift=3):
    result = ""
    for char in text:
        if char.isalpha():
            # On gère les majuscules (code ASCII 65-90)
            start = ord('A') if char.isupper() else ord('a')
            # Calcul du décalage circulaire
            new_char = chr((ord(char) - start + shift) % 26 + start)
            result += new_char
        else:
            result += char # On ne touche pas aux espaces/ponctuation
    return result

def caesar_decode(text, shift=3):
    # Déchiffrer, c'est décaler dans l'autre sens
    return caesar_encode(text, -shift)
=======
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
>>>>>>> christian
