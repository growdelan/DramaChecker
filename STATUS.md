# Aktualny stan projektu

## Co działa
- odczyt listy dram z Google Sheets przez konto serwisowe
- parsowanie stron DramaQueen i wykrywanie nowych odcinków
- aktualizacja kolumn z odcinkami w arkuszu
- wysyłka raportu e-mail HTML
- automatyczne logowanie do DramaQueen przez Playwright
- automatyczne pobranie pełnego zestawu cookie przeglądarki i przekazanie ich do `requests.Session`
- ponowne logowanie po wykryciu utraty autoryzacji
- retry odzyskania sesji dla chwilowych błędów logowania/cookie
- ponowienie sprawdzenia tego samego serialu po udanym odzyskaniu sesji
- ścisłe wykrywanie odcinków tylko dla etykiet dokładnie równych `Odcinek <numer>`

## Co jest skończone
- Milestone 0.5
- Milestone 1.0
- Milestone 1.1
- Milestone 1.2
- Milestone 1.3
- PRD dla automatycznego logowania: `prd/001-auto-cookie-login-prd.md`
- PRD retry autoryzacji: `prd/002-auth-retry-for-first-series-prd.md`
- PRD ścisłego parsowania etykiet odcinków: `prd/003-strict-episode-label-parsing-prd.md`
- testy jednostkowe dla logiki sesji, retry logowania i scenariuszy wyczerpania retry
- smoke test głównego przepływu `process_user()` bez realnego IO
- testy jednostkowe i smoke test dla etykiet odcinków z dodatkowymi opisami

## Co jest w trakcie
- brak aktywnego wdrożenia; bieżąca praca została domknięta na poziomie kodu i dokumentacji

## Co jest następne
- brak zaplanowanych milestone'ów; kolejny zakres wymaga dopisania nowego PRD lub milestone'u
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
- wdrożono retry odzyskania sesji (2 próby) w ścieżce sprawdzania serialu
- dodano testy `unittest` dla scenariusza: pierwsza próba logowania nieudana, druga udana
- dodano test `unittest` dla scenariusza: sesja nadal wymaga logowania po wyczerpaniu retry
- potwierdzono poprawny realny przebieg `uv run python main.py` z odzyskaniem sesji i wysyłką e-mail
- wdrożono ścisłe parsowanie etykiet odcinków i ignorowanie dopisków typu `Premiera w Korei: ...`
- dodano testy `unittest` i smoke test dla przypadku `Climax`, który wcześniej fałszywie wykrywał nowy odcinek
