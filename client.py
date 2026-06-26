import socket
import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from cryptography.fernet import Fernet

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

nume_utilizator = ""
client_socket = None
cipher = None

app = ctk.CTk()
app.title("Ephemera - CLIENT LOGIN")
app.geometry("350x450")
app.resizable(False, False)

def pornire_chat():
    global client_socket, cipher, nume_utilizator

    for widget in app.winfo_children():
        widget.destroy()

    app.title(f"Ephemera Terminal - Teren ({nume_utilizator})")
    app.geometry("500x700")
    app.resizable(True, True)
        
    chat_box = ctk.CTkTextbox(app, font=("Helvetica", 14), text_color="#ffffff", state="disabled")
    chat_box.pack(padx=20, pady=(20, 10), fill=tk.BOTH, expand=True)    

    chat_box.tag_config("me", foreground="green")
    chat_box.tag_config("alerta", foreground="#ff4444")

    def primeste_mesaje():
        while True:
            try:
                date_criptate = client_socket.recv(1024)
                if not date_criptate:
                    break
            
                mesaj_descifrat = cipher.decrypt(date_criptate).decode('utf-8')
                
                chat_box.configure(state="normal")
                if "[ALERTĂ: URGENȚĂ DETECTATĂ!]" in mesaj_descifrat:
                    chat_box.insert(tk.END, mesaj_descifrat + "\n", "alerta")
                else:
                    chat_box.insert(tk.END, mesaj_descifrat + "\n")
                chat_box.configure(state="disabled")
            except Exception:
                chat_box.configure(state="normal")
                chat_box.insert(tk.END, "[SISTEM] Conexiunea a fost întreruptă.\n")
                chat_box.configure(state="disabled")
                break

    def trimite_mesaj(event=None):
        mesaj = input_box.get()
        if mesaj:
            try:
                mesaj_criptat = f"{nume_utilizator}: {mesaj}"
                mesaj_criptat = cipher.encrypt(mesaj_criptat.encode('utf-8'))

                client_socket.send(mesaj_criptat)

                chat_box.configure(state="normal")
                chat_box.insert(tk.END, f"Tu: {mesaj}\n", "me")
                chat_box.configure(state="disabled")
                chat_box.yview(tk.END)
                input_box.delete(0, tk.END)
            except Exception:
                chat_box.configure(state="normal")
                chat_box.insert(tk.END, "[SISTEM] Eroare: Server-ul este offline.\n")
                chat_box.configure(state="disabled")

    frame_jos = ctk.CTkFrame(app, fg_color="transparent")
    frame_jos.pack(padx=20, pady=(0, 20), fill=tk.X)

    input_box = ctk.CTkEntry(frame_jos, font=("Helvetica", 14), placeholder_text="Transmite un mesaj...", height=40)
    input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    input_box.bind("<Return>", trimite_mesaj)

    buton_trimite = ctk.CTkButton(frame_jos, text="TRIMITE", font=("Arial", 14, "bold"), command=trimite_mesaj, width=120, height=40)
    buton_trimite.pack(side=tk.RIGHT)

    threading.Thread(target=primeste_mesaje, daemon=True).start()
    app.mainloop()
    client_socket.close()

def incearca_login():
    global nume_utilizator, client_socket, cipher
    nume = entry_user.get()
    parola = entry_pass.get()
    pin = entry_pin.get().replace(" ", "")

    if not nume or not parola:
        messagebox.showwarning("Atenție", "Te rugăm să completezi toate câmpurile, inclusiv PIN-ul!")
        return
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 8080))
        date_login = f"{nume}:{parola}:{pin}"
        client_socket.send(date_login.encode('utf-8'))

        raspuns = client_socket.recv(1024).decode('utf-8')

        if raspuns.startswith("SUCCES:"):
            cheie_primita = raspuns.split(":")[1].encode('utf-8')
            cipher = Fernet(cheie_primita)
            nume_utilizator = nume
            messagebox.showinfo("Succes", f"Autentificare reușită! Bine ai venit, {nume_utilizator}!")
            pornire_chat()
        elif raspuns == "DEJA_LOGAT":
            messagebox.showerror("Acces Respins", "Acest utilizator este deja conectat!")
            client_socket.close()
        else:
            messagebox.showerror("Acces Respins", "Nume sau parolă incorecte!")
            client_socket.close()

    except Exception as e:
        messagebox.showerror("Eroare Conexiune", f"Nu m-am putut conecta la server: {e}")

titlu = ctk.CTkLabel(app, text="Ephemera\n[UNITATE TEREN]", font=("Helvetica", 20, "bold"))
titlu.pack(pady=(50, 30))

entry_user = ctk.CTkEntry(app, font=("Helvetica", 14), placeholder_text="Indicativ Utilizator", width=250)
entry_user.pack(pady=10)

entry_pass = ctk.CTkEntry(app, font=("Helvetica", 14), placeholder_text="Parolă", show="*", width=250)
entry_pass.pack(pady=10)
entry_pass.bind("<Return>", lambda event: incearca_login())

entry_pin = ctk.CTkEntry(app, font=("Helvetica", 14), placeholder_text="Cod 2FA (Google Auth)", width=250)
entry_pin.pack(pady=10)
entry_pin.bind("<Return>", lambda event: incearca_login())

buton_login = ctk.CTkButton(app, text="AUTENTIFICARE", font=("Helvetica", 14, "bold"), command=incearca_login, width=250)
buton_login.pack(pady=30)

app.mainloop()