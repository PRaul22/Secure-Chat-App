import socket
import redis
import threading
import tkinter as tk
import customtkinter as ctk
import bcrypt
from tkinter import messagebox
from cryptography.fernet import Fernet
import joblib
import pyotp

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

nume_utilizator = ""
conexiuni_clienti = []
utilizatori_activi = set()
cipher = None

try:
    db = redis.Redis(host='localhost', port=6379, decode_responses=True)
    db.ping()
except Exception as e:
    print(f"[Eroare] Nu am putut conecta la Redis: {e}")

app = ctk.CTk()
app.title("Zero-Trace - SERVER LOGIN")
app.geometry("350x450")
app.resizable(False, False)

try:
    model_nlp = joblib.load('model_tactic_nlp.pkl')
    print("[SISTEM] Modelul NLP a fost încărcat cu succes.")
except Exception as e:
    print(f"[Avertisment] Nu am putut încărca modelul NLP: {e}")
    model_nlp = None

def pornire_chat():
    global nume_utilizator
    lista_vizibila = [False]

    for widget in app.winfo_children():
        widget.destroy()
        
    app.title(f"Ephemera Terminal - Server ({nume_utilizator})")
    app.geometry("500x700")
    app.resizable(True, True)
    
    frame_stanga = ctk.CTkFrame(app, fg_color="transparent")
    frame_stanga.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

    frame_dreapta = ctk.CTkFrame(app, width=200)

    titlu_lista = ctk.CTkLabel(frame_dreapta, text="UNITĂȚI ACTIVE", font=("Helvetica", 14, "bold"), text_color="#28a745")
    titlu_lista.pack(pady=10)

    lista_utilizatori = ctk.CTkTextbox(frame_dreapta, font=("Helvetica", 14), width=180, state="disabled")
    lista_utilizatori.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    lista_utilizatori.tag_config("verde", foreground="#28a745")

    def toggle_lista():
        if not lista_vizibila[0]:
            app.geometry("750x700")
            frame_dreapta.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 20), pady=20)
            buton_unitati.configure(text="ASCUNDE UNITĂȚI 👥")
            actualizeaza_lista()
            lista_vizibila[0] = True
        else:
            frame_dreapta.pack_forget()
            app.geometry("500x700")
            buton_unitati.configure(text="VEZI UNITĂȚI 👥")
            lista_vizibila[0] = False

    def actualizeaza_lista():
        lista_utilizatori.configure(state="normal")
        lista_utilizatori.delete("0.0", tk.END)
        if len(utilizatori_activi) == 0:
            lista_utilizatori.insert(tk.END, "Nicio unitate.\n")
        else:
            for u in utilizatori_activi:
                lista_utilizatori.insert(tk.END, "● ", "verde")
                lista_utilizatori.insert(tk.END, f"{u}\n")
        lista_utilizatori.configure(state="disabled")

    buton_unitati = ctk.CTkButton(frame_stanga, text="VEZI UNITĂȚI 👥", font=("Helvetica", 12), 
                                  command=toggle_lista, fg_color="#333333", hover_color="#444444", height=30)
    buton_unitati.pack(pady=(0, 10), anchor="e")

    chat_box = ctk.CTkTextbox(frame_stanga, font=("Helvetica", 14), text_color="#ffffff", state="disabled")
    chat_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    chat_box.tag_config("me", foreground="green")
    chat_box.tag_config("alerta", foreground="#ff4444")

    frame_jos = ctk.CTkFrame(frame_stanga, fg_color="transparent")
    frame_jos.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 0))

    input_box = ctk.CTkEntry(frame_jos, font=("Helvetica", 14), placeholder_text="Așteptare conexiuni...", height=40)
    input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    input_box.configure(state="disabled")

    def trimite_mesaj(event=None):
        mesaj = input_box.get()
        if mesaj:
            try:
                mesaj_formatat = f"{nume_utilizator}: {mesaj}"
                mesaj_criptat = cipher.encrypt(mesaj_formatat.encode('utf-8'))

                for client in conexiuni_clienti:
                    try: client.send(mesaj_criptat)
                    except: pass

                chat_box.configure(state="normal")
                chat_box.insert(tk.END, f"Tu: {mesaj}\n", "me")
                chat_box.configure(state="disabled")
                chat_box.yview(tk.END)
                input_box.delete(0, tk.END)
    
            except Exception as e:
                print(f"Eroare trimitere: {e}")
    
    input_box.bind("<Return>", trimite_mesaj)
    buton_trimite = ctk.CTkButton(frame_jos, text="TRIMITE", font=("Arial", 14, "bold"), 
                                  command=trimite_mesaj, state="disabled", width=120, height=40)
    buton_trimite.pack(side=tk.RIGHT)

    def logica_retea_server():
        global conexiuni_clienti, cipher
        try:
            cheie_dinamica = Fernet.generate_key()
            cipher = Fernet(cheie_dinamica)

            print(f"\n[SECURITATE] Cheia secretă a fost generată pentru această sesiune:")
            print(f" -> {cheie_dinamica.decode('utf-8')}")

            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('127.0.0.1', 8080))
            server_socket.listen(10)

            chat_box.configure(state="normal")
            chat_box.insert(tk.END, "[SISTEM] Aștept conexiuni pe portul 8080...\n")
            chat_box.configure(state="disabled")

            input_box.configure(state="normal", placeholder_text="Scrie un mesaj...")
            buton_trimite.configure(state="normal")

            def gestioneaza_client(c_loc, n_client):
                while True:
                    try:
                        date_criptate = c_loc.recv(1024)
                        if not date_criptate: break
                        mesaj_descifrat = cipher.decrypt(date_criptate).decode('utf-8')
                        
                        doar_textul = mesaj_descifrat.split(": ", 1)[1] if ": " in mesaj_descifrat else mesaj_descifrat

                        if model_nlp:
                            predictie = model_nlp.predict([doar_textul])[0]
                            if predictie == 1:
                                mesaj_descifrat = "[ALERTĂ: URGENȚĂ DETECTATĂ!] " + mesaj_descifrat
                                date_criptate = cipher.encrypt(mesaj_descifrat.encode('utf-8'))

                        chat_box.configure(state="normal")
                        if "[ALERTĂ: URGENȚĂ DETECTATĂ!]" in mesaj_descifrat:
                            chat_box.insert(tk.END, mesaj_descifrat + "\n", "alerta")
                        else:
                            chat_box.insert(tk.END, mesaj_descifrat + "\n")
                        chat_box.configure(state="disabled")
                        chat_box.yview(tk.END)

                        for c in conexiuni_clienti:
                            if c != c_loc:
                                try: c.send(date_criptate)
                                except: pass
                    except: break
                
                if c_loc in conexiuni_clienti: conexiuni_clienti.remove(c_loc)
                if n_client in utilizatori_activi: utilizatori_activi.remove(n_client)
                c_loc.close()

                chat_box.configure(state="normal")
                chat_box.insert(tk.END, f"[SISTEM] {n_client} a părăsit rețeaua.\n")
                chat_box.configure(state="disabled")

                actualizeaza_lista()

            while True:
                conn_loc, address = server_socket.accept()
                date_login = conn_loc.recv(1024).decode('utf-8')
                
                if date_login.count(":") == 2:
                    nume_client, parola_client, pin_client = date_login.split(":")
                    
                    if nume_client in utilizatori_activi:
                        conn_loc.send("DEJA_LOGAT".encode('utf-8'))
                        conn_loc.close()
                        continue

                    hash_salvat = db.get(f"user:{nume_client}")
                    
                    if hash_salvat and bcrypt.checkpw(parola_client.encode('utf-8'), hash_salvat.encode('utf-8')):
                        
                        cheie_2fa = db.get(f"user_2fa:{nume_client}")
                        
                        if not cheie_2fa:
                            print(f"[ALARMĂ] Contul {nume_client} e prea vechi și NU are 2FA configurat!")
                            conn_loc.send("EROARE".encode('utf-8'))
                            conn_loc.close()
                            continue

                        totp = pyotp.TOTP(cheie_2fa)
                        
                        if totp.verify(pin_client):
                        
                            utilizatori_activi.add(nume_client)
                        
                            pachet_raspuns = f"SUCCES:{cheie_dinamica.decode('utf-8')}"
                            conn_loc.send(pachet_raspuns.encode('utf-8'))
                        
                            print(f"[SECURITATE] {nume_client} a trecut de ambele filtre (Parolă + 2FA)!")
                            print(f"[SECURITATE] Am trimis cheia către '{nume_client}'. Conversația este acum securizată!")
                            conexiuni_clienti.append(conn_loc)
                        
                            chat_box.configure(state="normal")
                            chat_box.insert(tk.END, f"[SISTEM] {nume_client} s-a autentificat cu succes!\n")
                            chat_box.configure(state="disabled")

                            actualizeaza_lista()
                        
                            threading.Thread(target=gestioneaza_client, args=(conn_loc, nume_client), daemon=True).start()
                        else:
                            print(f"[ALARMĂ] {nume_client} a introdus un PIN 2FA invalid!")
                            conn_loc.send("EROARE".encode('utf-8'))
                            conn_loc.close()
                    else:
                        conn_loc.send("EROARE".encode('utf-8'))
                        conn_loc.close()
                else:
                    conn_loc.send("EROARE".encode('utf-8'))
                    conn_loc.close()

        except Exception as e:
            print(f"[Eroare] Server: {e}")

    threading.Thread(target=logica_retea_server, daemon=True).start()
    app.mainloop()

def incearca_login():
    global nume_utilizator
    nume = entry_user.get()
    parola = entry_pass.get()

    if not nume or not parola:
        messagebox.showwarning("Atenție", "Te rugăm să completezi atât numele, cât și parola!")
        return
    
    try:
        parola_salvata_hash = db.get(f"user:{nume}")

        if parola_salvata_hash is None:
            messagebox.showerror("Eroare", "Numele de utilizator nu există. Te rugăm să încerci din nou.")
        else:
            parola_bytes = parola.encode('utf-8')
            hash_bytes = parola_salvata_hash.encode('utf-8')

            if bcrypt.checkpw(parola_bytes, hash_bytes):
                nume_utilizator = nume
                utilizatori_activi.add(nume)
                messagebox.showinfo("Succes", f"Autentificare reușită! Bine ai venit, {nume_utilizator}!")
                pornire_chat()
            else:
                messagebox.showerror("Eroare", "Parola este incorectă. Te rugăm să încerci din nou.")
    except Exception as e:
        messagebox.showerror("Eroare", f"A apărut o eroare la autentificare: {e}")

titlu = ctk.CTkLabel(app, text="Ephemera\n[CENTRUL DE COMANDĂ]", font=("Helvetica", 20, "bold"))
titlu.pack(pady=(50, 30))

entry_user = ctk.CTkEntry(app, font=("Helvetica", 14), placeholder_text="Indicativ Utilizator", width=250)
entry_user.pack(pady=10)

entry_pass = ctk.CTkEntry(app, font=("Helvetica", 14), placeholder_text="Parolă", show="*", width=250)
entry_pass.pack(pady=10)
entry_pass.bind("<Return>", lambda event: incearca_login())

buton_login = ctk.CTkButton(app, text="AUTENTIFICARE", font=("Helvetica", 14, "bold"), command=incearca_login, width=250)
buton_login.pack(pady=30)

app.mainloop() 


