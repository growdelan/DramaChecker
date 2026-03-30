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

## Milestone 1.1: Dokumentacja i testy dla automatycznego logowania (done)

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
- README uzupełnione o konfigurację i uruchamianie Playwright
- istnieją testy jednostkowe oraz smoke test `process_user()` bez realnego IO

---

## Milestone 1.2: Retry odzyskania sesji dla chwilowych błędów logowania (done)

Cel:
- ograniczyć losowe błędy typu `Po logowaniu nie znaleziono wymaganych cookie sesyjnych`
- zapewnić ponowienie sprawdzenia serialu po chwilowej awarii odzyskania sesji

Definition of Done:
- dla chwilowego błędu logowania/cookie aplikacja wykonuje dodatkową próbę odzyskania sesji
- po udanym retry aplikacja ponawia pobranie strony tego samego serialu
- po wyczerpaniu limitu prób aplikacja zwraca czytelny błąd końcowy
- istnieją testy `unittest` dla scenariusza: pierwsza próba nieudana, druga udana

Zakres:
- dodanie kontrolowanego retry w ścieżce odzyskiwania sesji
- ponowienie sprawdzenia tego samego serialu po udanym odzyskaniu sesji
- dodanie logów diagnostycznych z numerem próby
- rozszerzenie testów jednostkowych o scenariusze retry

Uwagi:
- zakres wynika z `prd/002-auth-retry-for-first-series-prd.md`
- poza zakresem: trwały cache cookie między uruchomieniami
- wdrożono retry odzyskania sesji z limitem prób oraz testy `unittest` dla scenariuszy błędów przejściowych i wyczerpania retry

---

## Milestone 1.3: Ścisłe wykrywanie odcinków bez dodatkowych opisów (done)

Cel:
- wyeliminować fałszywe wykrycia odcinków dla etykiet zawierających dodatkowy opis, takich jak `Premiera w Korei: ...`
- uznawać za istniejące wyłącznie odcinki oznaczone dokładnie jako `Odcinek <numer>`

Definition of Done:
- parser uznaje za odcinek tylko element, którego pełny tekst po normalizacji jest dokładnie równy `Odcinek <numer>`
- etykiety z dodatkowymi dopiskami nie wpływają ani na `latest_ready`, ani na `max_found`
- istnieją testy `unittest` dla scenariuszy z dodatkowymi opisami oraz scenariuszy mieszanych
- brak regresji dla istniejących testów prostych etykiet i blokad z obrazkiem

Zakres:
- doprecyzowanie logiki parsowania etykiet odcinków
- utrzymanie obecnego rozróżnienia między odcinkiem gotowym i zablokowanym przez obrazek
- dodanie testów dla etykiet typu `Odcinek 6 Premiera w Korei: 31.03.2026`

Uwagi:
- zakres wynika z `prd/003-strict-episode-label-parsing-prd.md`
- wdrożono ścisłe dopasowanie etykiet `Odcinek <numer>` oraz testy dla przypadków z dodatkowymi opisami
- potwierdzony przypadek błędu dotyczył strony `Climax`, gdzie `Odcinek 6 Premiera w Korei: 31.03.2026` był błędnie liczony jako dostępny odcinek
