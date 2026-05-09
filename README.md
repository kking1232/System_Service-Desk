System Service Desk

System do zarządzania zgłoszeniami serwisowymi, stworzony jako projekt inżynierski. Aplikacja umożliwia sprawną komunikację między konsultantami a działem IT, automatyzację procesów oraz raportowanie wydajności.

Główne Funkcjonalności
1. Zarządzanie Zgłoszeniami: Tworzenie, edycja i monitorowanie statusu ticketów.
2. Automatyczne Numerowanie: Każda sprawa otrzymuje unikalny numer w formacie IT-YYYY-MM-DD-XXX.
3. System Powiadomień: Powiadomienia w czasie rzeczywistym o zmianie statusu lub nowym komentarzu.
4. Raportowanie SLA: Automatyczne generowanie raportów Excel z obliczonym czasem realizacji zgłoszeń.
5. Obsługa Załączników: System Drag&Drop do przesyłania dokumentacji technicznej i zrzutów ekranu.

Technologie
1. Backend: Python 3.10 + Flask
2. Baza danych: MySQL 8.0 + SQLAlchemy
3. Frontend: HTML5, CSS3, JavaScript
4. Migracje: Flask-Migrate
5. Bezpieczeństwo: Werkzeug (Hashing), TLS/SSL

Architektura Projektu
Projekt realizuje zasadę Separation of Concerns:
- app.py - główny serwer, kontroler tras i konfiguracja HTTPS.
- models.py - schemat bazy danych i relacji ORM.
- utils.py - moduły pomocnicze, obsługa logów i formatowanie danych.
- templates/ - warstwa prezentacji (Jinja2).
- static/ - zasoby wizualne (CSS, JS, Uploads).

Konfiguracja sieciowa

System został zaprojetkowany do pracy w odizolowanych segmentach sieciowych:
- VLAN 10: PC_Konsultant (192.168.10.10).
- VLAN 20: Server_FLASK (192.168.20.10).
- VLAN 30: Server_SQL (192.168.30.10).
- VLAN 99: Admin_IT (192.168.99.10).
- HTTPS: Komunikacja szyfrowana na porcie 443.

Instalacja
```bash
   git clone [https://github.com/kking1232/ServiceDesk.git](https://github.com/kking1232/ServiceDesk.git)