def cesar_chiffrer(texte, decalage):
    resultat = ""
    for char in texte:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            resultat += chr((ord(char) - base + decalage) % 26 + base)
        else:
            resultat += char
    return resultat

def cesar_dechiffrer(texte, decalage):
    return cesar_chiffrer(texte, -decalage)



