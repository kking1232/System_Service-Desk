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
2. Baza danych: MySQL + SQLAlchemy
3. Frontend: HTML5, CSS3, JavaScript
4. Migracje: Flask-Migrate
5. Bezpieczeństwo: Haszowanie haseł (Werkzeug), ochrona sesji (Secret Key).

Architektura Projektu
Projekt realizuje zasadę Separation of Concerns:
- models.py - Definicja schematu bazy danych i relacji.
- app.py - Logika serwerowa i kontroler tras.
- utils.py - Moduły pomocnicze i logika biznesowa.
- static/ - Odseparowane zasoby CSS i JS.

Instalacja
1. Sklonuj repozytorium.
2. Zainstaluj biblioteki: pip install -r requirements.txt.
3. Skonfiguruj bazę danych w app.py.
4. Uruchom aplikację: python app.py.