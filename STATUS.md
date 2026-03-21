# Aktualny stan projektu

## Co działa
- odczyt listy dram z Google Sheets przez konto serwisowe
- parsowanie stron DramaQueen i wykrywanie nowych odcinków
- aktualizacja kolumn z odcinkami w arkuszu
- wysyłka raportu e-mail HTML
- automatyczne logowanie do DramaQueen przez Playwright
- automatyczne pobranie cookie sesyjnych i przekazanie ich do `requests.Session`
- ponowne logowanie po wykryciu utraty autoryzacji

## Co jest skończone
- Milestone 0.5
- Milestone 1.0
- PRD dla automatycznego logowania: `prd/001-auto-cookie-login-prd.md`
- testy jednostkowe dla logiki sesji i retry logowania

## Co jest w trakcie
- porządkowanie dokumentacji operacyjnej po wdrożeniu logowania przez Playwright

## Co jest następne
- Milestone 1.1: uzupełnienie README i pełniejszego zestawu testów
- doprecyzowanie przykładowej konfiguracji użytkowników na bazie `users.example.json`
- ewentualne wydzielenie logiki uwierzytelnienia z `main.py` bez zmiany zachowania

## Blokery i ryzyka
- brak obsługi CAPTCHA i 2FA
- selektory logowania mogą wymagać aktualizacji, jeśli formularz DramaQueen się zmieni
- projekt nadal ma całą logikę aplikacyjną skupioną w `main.py`

## Ostatnie aktualizacje
- dodano logowanie przez Playwright i automatyczne odświeżanie sesji
- potwierdzono działanie na realnym logowaniu, odczycie arkusza `dramy` i wysyłce e-mail
- dodano `users.example.json` oraz pozostawiono prawdziwy `users.json` poza repo
