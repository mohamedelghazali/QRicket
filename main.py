import sqlite3
import uuid
import qrcode
from tkinter import *
from tkinter import messagebox

# Fonction pour générer un QR code
def generate_qr(text, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    img.save(filename)

# Fonction pour acheter un billet
def acheter_billet():
    try:
        seance_id = int(entry_seance_id.get())
        with sqlite3.connect('cinema.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT places_vendues, max_places FROM seances WHERE id = ?', (seance_id,))
            result = cursor.fetchone()

            if result is None:
                messagebox.showerror("Erreur", "Séance introuvable.")
                return

            places_vendues, max_places = result

            if places_vendues >= max_places:
                messagebox.showinfo("Complet", "Plus de places disponibles.")
                return

            qr_code = str(uuid.uuid4())
            generate_qr(qr_code, f"ticket_{seance_id}.png")

            cursor.execute('INSERT INTO tickets (seance_id, qr_code) VALUES (?, ?)', (seance_id, qr_code))
            cursor.execute('UPDATE seances SET places_vendues = places_vendues + 1 WHERE id = ?', (seance_id,))
            
            conn.commit()
        
        messagebox.showinfo("Succès", f"Billet acheté ! QR code : {qr_code}")
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer un ID de séance valide.")

# Fonction pour vérifier le ticket
def verifier_ticket():
    qr_code = entry_qr_code.get()
    with sqlite3.connect('cinema.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tickets WHERE qr_code = ?', (qr_code,))
        ticket = cursor.fetchone()

        if ticket:
            messagebox.showinfo("Succès", "Ticket valide ! Bon film !")
            cursor.execute('DELETE FROM tickets WHERE qr_code = ?', (qr_code,))
            conn.commit()
        else:
            messagebox.showerror("Erreur", "Ticket invalide ou déjà utilisé.")

# Fonction pour créer la base de données
def creer_base_de_donnees():
    with sqlite3.connect('cinema.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS seances (
            id INTEGER PRIMARY KEY,
            nom TEXT NOT NULL,
            date TEXT NOT NULL,
            heure TEXT NOT NULL,
            places_vendues INTEGER DEFAULT 0,
            max_places INTEGER DEFAULT 400
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seance_id INTEGER,
            qr_code TEXT UNIQUE,
            FOREIGN KEY(seance_id) REFERENCES seances(id)
        )
        ''')

        for i in range(1, 21):
            cursor.execute('''
            INSERT OR IGNORE INTO seances (id, nom, date, heure, places_vendues, max_places)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (i, f"Séance {i}", "2024-11-01", f"{10+i}:00", 0, 400))

        conn.commit()

# Interface graphique avec Tkinter
root = Tk()
root.title("Gestion de Billetterie - Cinéma")

# Créer la base de données au démarrage
creer_base_de_donnees()

# Interface pour l'achat de billets
Label(root, text="Achat de billet", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

Label(root, text="ID de la séance :").grid(row=1, column=0, padx=10, pady=5, sticky=E)
entry_seance_id = Entry(root)
entry_seance_id.grid(row=1, column=1, padx=10, pady=5)

Button(root, text="Acheter", command=acheter_billet).grid(row=2, column=0, columnspan=2, pady=10)

# Interface pour la vérification de billets
Label(root, text="Vérification de ticket", font=("Arial", 16)).grid(row=3, column=0, columnspan=2, pady=10)

Label(root, text="QR Code :").grid(row=4, column=0, padx=10, pady=5, sticky=E)
entry_qr_code = Entry(root)
entry_qr_code.grid(row=4, column=1, padx=10, pady=5)

Button(root, text="Vérifier", command=verifier_ticket).grid(row=5, column=0, columnspan=2, pady=10)

# Lancer l'interface graphique
root.mainloop()
