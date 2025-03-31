import socket
import time
import datetime
import threading
import csv
import re

ziel = "8.8.8.8"
port = 53
logdatei = "netzwerk_log.csv"
timeout_schwelle = 1.0

# TCP-Verbindung aufbauen
def check_tcp_connection(host, port, result):
    try:
        start = time.time()
        with socket.create_connection((host, port), timeout=timeout_schwelle):
            dauer = int((time.time() - start) * 1000)
            result.append(f"OK ({dauer}ms)")
    except socket.timeout:
        result.append("Timeout (abgebrochen)")
    except Exception as e:
        result.append(f"Fehler ({str(e)})")

# Timeout behandeln
def check_with_timeout():
    result = []
    thread = threading.Thread(target=check_tcp_connection, args=(ziel, port, result))
    thread.daemon = True
    thread.start()
    thread.join(timeout=timeout_schwelle)
    if not result:
        return "Timeout (abgebrochen)"
    return result[0]

# Log-Datei vorbereiten
with open(logdatei, "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Datum", "Uhrzeit", "Status", "Latenz (ms)"])

print("Starte Monitoring. Logge alle 0.5 Sekunden...")

# Haupt-Loop
with open(logdatei, "a", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    while True:
        jetzt = datetime.datetime.now()
        datum = jetzt.strftime("%Y-%m-%d")
        uhrzeit = jetzt.strftime("%H:%M:%S.%f")[:-3]
        status = check_with_timeout()

        # Latenz extrahieren (wenn vorhanden)
        match = re.search(r"\((\d+)ms\)", status)
        latenz = match.group(1) if match else ""

        logeintrag = [datum, uhrzeit, status, latenz]
        print(f"{datum} {uhrzeit} - {status}")
        
        writer.writerow(logeintrag)
        time.sleep(0.5)
