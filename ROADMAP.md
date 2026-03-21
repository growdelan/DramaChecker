# Roadmapa (milestones)

## Statusy milestone’ów
Dozwolone statusy:
- planned
- in_progress
- done
- blocked

---

## Milestone 0.5: Minimal end-to-end slice (done)

Cel:
- aplikacja uruchamia się
- wykonuje jedno bardzo proste zadanie
- zwraca poprawny wynik

Definition of Done:
- aplikację da się uruchomić jednym poleceniem (opisanym w README.md)
- istnieje co najmniej jeden smoke test
- testy przechodzą lokalnie
- brak placeholderów w kodzie

Zakres:
- minimalny entrypoint aplikacji
- minimalna logika domenowa
- minimalna obsługa IO (jeśli dotyczy)
- smoke test end-to-end

---

## Milestone <numer>: <nazwa> (<status>)

Cel:
Definition of Done:
Zakres:
Uwagi:

---

## Milestone 1.0: Automatyczne logowanie do serwisu przez Playwright (done)

Cel:
- dodać mechanizm samodzielnego logowania do serwisu źródłowego bez ręcznego wpisywania cookie do `.env`
- uzyskać poprawne cookie sesyjne przez Playwright i przekazać je do istniejącej sesji HTTP

Definition of Done:
- aplikacja potrafi zalogować się loginem i hasłem do serwisu przez Playwright
- cookie pozyskane po logowaniu są używane przez istniejący mechanizm pobierania stron
- istnieje wykrywanie utraty autoryzacji i automatyczne ponowne logowanie
- błędy logowania są logowane oraz przekazywane do istniejącego mechanizmu raportowania

Zakres:
- dodanie komponentu logowania przeglądarkowego opartego na Playwright
- odczyt cookie po zalogowaniu i mapowanie ich do `requests.Session`
- wykrywanie nieważnej sesji i uruchamianie ponownego logowania
- zachowanie ręcznego trybu cookie tylko jako ścieżki awaryjnej

Uwagi:
- zakres wynika z `prd/001-auto-cookie-login-prd.md`
- poza zakresem: CAPTCHA i 2FA
- wdrożone oraz sprawdzone na realnym logowaniu, odczycie arkusza i wysyłce e-mail

---

## Milestone 1.1: Dokumentacja i testy dla automatycznego logowania (planned)

Cel:
- domknąć wdrożenie automatycznego logowania od strony jakościowej i operacyjnej

Definition of Done:
- README opisuje nowe zmienne środowiskowe i sposób uruchomienia z Playwright
- istnieją testy dla logiki obsługi sesji oraz scenariuszy utraty autoryzacji bez realnego IO
- istnieje smoke test potwierdzający integrację nowego mechanizmu z głównym przepływem aplikacji

Zakres:
- aktualizacja dokumentacji operacyjnej o nowe wymagania środowiskowe
- dodanie testów jednostkowych i smoke testów z użyciem stubów/fake’ów
- weryfikacja, że mechanizm logowania nie narusza obecnego przepływu przetwarzania użytkowników

Uwagi:
- milestone zależny od realizacji Milestone 1.0
