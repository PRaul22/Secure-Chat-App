import redis
import bcrypt
import pyotp
import qrcode
import os

def adauga_soldat():
    print("PANOU DE COMANDĂ: ÎNREGISTRARE SOLDAT NOU")
    try:
        db = redis.Redis(host='localhost', port=6379, decode_responses=True)
        db.ping() 

        nume = input("Introdu numele noului soldat: ")
        parola = input("Introdu parola: ")

        if db.exists(f"user:{nume}"):
            print(f"[!] Soldatul '{nume}' există deja în baza de date!")
            return

        sare = bcrypt.gensalt()
        hash_parola = bcrypt.hashpw(parola.encode('utf-8'), sare)
        db.set(f"user:{nume}", hash_parola.decode('utf-8'))

        cheie_2fa = pyotp.random_base32()
        db.set(f"user_2fa:{nume}", cheie_2fa)

        uri_qr = pyotp.totp.TOTP(cheie_2fa).provisioning_uri(name=nume, issuer_name="Ephemera")
        
        print(f"\n[SUCCES] Soldatul '{nume}' a fost salvat securizat!")
        print(f"\n[ACȚIUNE NECESARĂ] Deschide Google Authenticator pe telefon, apasă pe '+' -> Introducere cheie de configurare.")
        print(f"Nume cont: Ephemera ({nume})")
        print(f"Cheie secretă: {cheie_2fa}")
        print("\n(Opțional) Dacă vrei codul QR, el s-a salvat în folder ca 'qr_soldat.png'")

        img = qrcode.make(uri_qr)
        img.save("qr_soldat.png")

        print(f"\n Acces aprobat: Soldatul '{nume}' a fost salvat securizat în baza de date!")

    except redis.ConnectionError:
        print("[EROARE] Serverul Redis nu este pornit!")

if __name__ == "__main__":
    adauga_soldat()