# Aktualny stan projektu

## Co działa
- odczyt listy dram z Google Sheets przez konto serwisowe
- parsowanie stron DramaQueen i wykrywanie nowych odcinków
- aktualizacja kolumn z odcinkami w arkuszu
- wysyłka raportu e-mail HTML
- automatyczne logowanie do DramaQueen przez Playwright
- automatyczne pobranie pełnego zestawu cookie przeglądarki i przekazanie ich do `requests.Session`
- ponowne logowanie po wykryciu utraty autoryzacji

## Co jest skończone
- Milestone 0.5
- Milestone 1.0
- Milestone 1.1
- PRD dla automatycznego logowania: `prd/001-auto-cookie-login-prd.md`
- testy jednostkowe dla logiki sesji i retry logowania
- smoke test głównego przepływu `process_user()` bez realnego IO

## Co jest w trakcie
- brak aktywnego wdrożenia; bieżąca praca została domknięta na poziomie kodu i dokumentacji

## Co jest następne
- doprecyzowanie przykładowej konfiguracji użytkowników na bazie `users.example.json`
- ewentualne wydzielenie logiki uwierzytelnienia z `main.py` bez zmiany zachowania
- ewentualna obsługa CAPTCHA i 2FA jako osobny zakres prac

## Blokery i ryzyka
- brak obsługi CAPTCHA i 2FA
- selektory logowania mogą wymagać aktualizacji, jeśli formularz DramaQueen się zmieni
- projekt nadal ma całą logikę aplikacyjną skupioną w `main.py`

## Ostatnie aktualizacje
- dodano logowanie przez Playwright i automatyczne odświeżanie sesji
- potwierdzono działanie na realnym logowaniu, odczycie arkusza `dramy` i wysyłce e-mail
- dodano `users.example.json` oraz pozostawiono prawdziwy `users.json` poza repo
- naprawiono przypadek `City Hunter` przez przekazywanie pełnego zestawu cookie z Playwright do `requests.Session`
- dodano smoke test `process_user()` oraz domknięto README dla Milestone 1.1
