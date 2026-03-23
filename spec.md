# Specyfikacja techniczna

## Cel
DramaChecker to skrypt automatyzujący kontrolę dostępności nowych odcinków K-dram śledzonych przez użytkownika.

Problem, który rozwiązuje:
- eliminuje ręczne sprawdzanie stron z odcinkami i ręczne porównywanie ich z własną listą obejrzanych epizodów
- utrzymuje stan śledzenia w arkuszu Google Sheets i generuje zbiorcze powiadomienie e-mail

Docelowy użytkownik:
- osoba lub mała grupa użytkowników prowadzących własne listy oglądanych dram w Google Sheets
- użytkownik techniczny lub półtechniczny, który potrafi skonfigurować zmienne środowiskowe, konto usługi Google i SMTP

Zakres obecnej implementacji:
- obsługa jednego lub wielu użytkowników
- odczyt listy seriali z Google Sheets
- pobranie stron odcinków z serwisu DramaQueen
- wykrycie najnowszego dostępnego odcinka i maksymalnej liczby znalezionych odcinków
- aktualizacja wybranych kolumn w arkuszu
- wysłanie e-maila HTML z listą nowych odcinków i problemów technicznych

Wdrożone rozszerzenie zakresu (PRD `001-auto-cookie-login-prd.md`):
- automatyczne logowanie do serwisu źródłowego przez Playwright
- samodzielne pobieranie i odświeżanie cookie sesyjnych
- przekazanie aktualnych cookie do istniejącego przepływu opartego na `requests.Session`

Wdrożone rozszerzenie zakresu (PRD `002-auth-retry-for-first-series-prd.md`):
- kontrolowane retry odzyskania sesji po chwilowym błędzie logowania/cookie
- ponowienie sprawdzenia tego samego serialu po udanym odzyskaniu sesji
- ograniczony limit prób i czytelne logowanie numeru próby

Poza zakresem:
- interfejs WWW, CLI z parserem argumentów lub panel administracyjny
- trwała baza danych poza Google Sheets
- integracje z innymi serwisami niż obecnie parsowany serwis źródłowy
- harmonogram uruchomień; uruchamianie zakłada zewnętrzny scheduler
- obsługa CAPTCHA i 2FA w ramach planowanego rozszerzenia logowania automatycznego

---

## Zakres funkcjonalny (high-level)
Główne use-case’i:
- użytkownik utrzymuje arkusz z listą śledzonych dram i stanem obejrzenia
- skrypt sprawdza strony seriali i wykrywa nowe odcinki
- skrypt aktualizuje w arkuszu kolumny z numerem odcinka dostępnego na stronie i łączną liczbą odcinków
- użytkownik otrzymuje wiadomość e-mail z listą pozycji wymagających obejrzenia
- użytkownik nie musi ręcznie aktualizować cookie w `.env`, ponieważ aplikacja sama odzyskuje sesję do serwisu źródłowego

Główne przepływy:
1. Start procesu i wczytanie konfiguracji z `.env` oraz opcjonalnie z pliku JSON dla wielu użytkowników.
2. Uwierzytelnienie do Google Sheets kontem serwisowym.
3. Odczyt wierszy arkusza i mapowanie kolumn po nazwach lub aliasach.
4. Pobranie HTML dla każdego nieukończonego serialu.
5. Analiza HTML i wykrycie najwyższego numeru odcinka oraz najwyższego numeru odcinka gotowego do obejrzenia.
6. Aktualizacja arkusza i przygotowanie modelu danych do e-maila.
7. Wysłanie raportu HTML albo zakończenie bez wysyłki, jeśli konfiguracja tego wymaga.

Aplikacja obecnie nie robi:
- nie zapisuje historii zmian ani audytu operacji
- nie rozróżnia typów błędów na poziomie retry/backoff/circuit breaker
- nie waliduje konfiguracji w sposób formalny przed startem

Wdrożone rozszerzenie wynikające z PRD `001-auto-cookie-login-prd.md`:
- automatyczne logowanie przez rzeczywistą przeglądarkę sterowaną Playwright
- wykrywanie utraty autoryzacji i automatyczne odświeżanie sesji
- pozostawienie ręcznie podanych cookie wyłącznie jako trybu awaryjnego
- przekazywanie pełnego zestawu cookie z przeglądarki do `requests.Session`, aby zachować dostęp do stron wymagających dodatkowego stanu sesji

Wdrożone rozszerzenie wynikające z PRD `002-auth-retry-for-first-series-prd.md`:
- dodatkowa próba odzyskania sesji dla chwilowych błędów logowania/cookie
- ponowienie pobrania strony tego samego serialu po udanym retry
- zakończenie błędem dopiero po wyczerpaniu limitu prób

---

## Architektura i przepływ danych
Architektura jest monolityczna i skryptowa. Cała logika znajduje się w jednym entrypoincie `main.py`.

1. Główne komponenty systemu
- loader konfiguracji środowiskowej i konfiguracji użytkowników
- klient Google Sheets oparty o `gspread`
- klient HTTP oparty o `requests.Session`
- parser HTML oparty o `BeautifulSoup`
- renderer e-maili HTML oparty o `jinja2.Template`
- nadawca e-maili oparty o `smtplib`
- komponent logowania przeglądarkowego i odświeżania sesji oparty o Playwright

2. Przepływ danych między komponentami
- konfiguracja wejściowa pochodzi ze zmiennych środowiskowych oraz opcjonalnego pliku JSON wskazanego przez `USERS_CONFIG`
- dane logowania do serwisu źródłowego są dostarczane przez zmienne środowiskowe
- dla każdego użytkownika skrypt otwiera wskazany arkusz i zakładkę
- przed pobieraniem stron aplikacja będzie weryfikować, czy ma ważną sesję do serwisu źródłowego
- jeśli sesja będzie nieważna, komponent Playwright wykona logowanie i zasili `requests.Session` pełnym zestawem aktualnych cookie z kontekstu przeglądarki
- dla błędów odzyskiwania sesji aplikacja wykonuje ograniczony retry, zanim zgłosi błąd końcowy (wdrożone w PRD `002-auth-retry-for-first-series-prd.md`)
- z arkusza pobierane są wszystkie wiersze i mapowane do modelu `SeriesRow`
- dla każdego aktywnego serialu wykonywane jest żądanie HTTP do strony odcinków
- HTML jest parsowany do wyniku `EpisodeCheckResult`
- wynik porównywany jest ze stanem w arkuszu, a różnice są zapisywane z powrotem do Google Sheets
- lista nowych odcinków i problemów trafia do szablonu HTML i dalej do SMTP

3. Granice odpowiedzialności
- Google Sheets pełni rolę źródła konfiguracji listy seriali oraz magazynu bieżącego stanu odcinków
- serwis zewnętrzny dostarcza tylko dane źródłowe HTML
- skrypt odpowiada za orkiestrację, interpretację HTML, synchronizację stanu oraz notyfikację
- SMTP odpowiada wyłącznie za dostarczenie raportu
- komponent Playwright odpowiada wyłącznie za uzyskanie i odświeżenie uwierzytelnionej sesji

Obecne ograniczenie architektoniczne:
- brak podziału na moduły domenowe, infrastrukturę i warstwę aplikacyjną utrudnia testowanie, rozwój i izolację błędów

---

## Komponenty techniczne
- `main.py`: jedyny entrypoint i miejsce całej logiki aplikacyjnej
- `SeriesRow`: model pojedynczego wiersza arkusza z logiką określającą, czy serial jest ukończony
- `EpisodeCheckResult`: model wyniku parsowania strony serialu
- `UserConfig`: model konfiguracji pojedynczego użytkownika
- `load_user_configs()`: ładowanie trybu jedno- i wieloużytkownikowego
- `map_headers()` i `read_series()`: odczyt i normalizacja struktury arkusza
- `build_requests_session()`: budowa sesji HTTP wraz z opcjonalnymi cookies do dostępu do serwisu
- `find_episodes()` i `extract_episode_number()`: wydobywanie informacji o odcinkach z HTML
- `process_user()`: główna orkiestracja przepływu dla pojedynczego użytkownika
- `build_email_html()` i `send_email()`: generowanie i wysyłka raportu HTML
- moduł logowania Playwright: uzyskanie cookie po zalogowaniu i przekazanie ich do sesji HTTP
- moduł translacji sesji przeglądarki: przeniesienie pełnego zestawu cookie do klienta `requests`
- mechanizm walidacji sesji: wykrycie utraty autoryzacji i wywołanie ponownego logowania
- mechanizm retry autoryzacji: ponowna próba odzyskania sesji i ponowienie sprawdzenia tego samego serialu po chwilowej awarii logowania/cookie

Zewnętrzne zależności wykonawcze:
- Google Sheets API przez konto serwisowe
- serwer SMTP
- dostęp HTTP do stron źródłowych
- zależność wykonawcza: przeglądarka uruchamiana przez Playwright do logowania do serwisu źródłowego

---

## Decyzje techniczne
1. Decyzja:
   Utrzymywanie stanu śledzenia seriali w Google Sheets zamiast w lokalnej bazie danych.
   Uzasadnienie:
   To najprostszy sposób edycji danych przez użytkownika bez budowy dodatkowego interfejsu.
   Konsekwencje:
   Schemat danych jest słabo typowany, zależny od nazw kolumn i podatny na błędy edycji ręcznej.

2. Decyzja:
   Implementacja całego przepływu w pojedynczym skrypcie `main.py`.
   Uzasadnienie:
   Dla małego projektu pozwala to szybko dostarczyć działający przepływ end-to-end.
   Konsekwencje:
   Rosnące sprzężenie utrudnia testowanie jednostkowe, refaktoryzację i rozwój kolejnych milestone’ów.

3. Decyzja:
   Parsowanie dostępności odcinków z HTML strony przez `BeautifulSoup` i prosty regex.
   Uzasadnienie:
   Źródło nie udostępnia w projekcie sformalizowanego API, więc HTML scraping jest najprostszą ścieżką integracji.
   Konsekwencje:
   Zmiany struktury HTML lub nazewnictwa odcinków mogą łatwo zepsuć detekcję.

4. Decyzja:
   Wysyłanie raportów przez SMTP z HTML renderowanym przez `jinja2`.
   Uzasadnienie:
   To lekka implementacja bez potrzeby zewnętrznego dostawcy API do maili.
   Konsekwencje:
   Poprawne działanie zależy od ręcznej konfiguracji SMTP i kompatybilności serwera z TLS/loginem.

5. Decyzja:
   Obsługa wielu użytkowników przez plik JSON wskazany w `USERS_CONFIG`.
   Uzasadnienie:
   Rozszerza istniejący skrypt bez przebudowy modelu uruchomienia i bez potrzeby wielu osobnych deploymentów.
   Konsekwencje:
   Konfiguracja nie jest walidowana schematem, a błędy wejścia wykrywane są dopiero w runtime.

6. Decyzja:
   Użycie zależności: `requests`, `beautifulsoup4`, `python-dotenv`, `gspread`, `google-auth`, `google-auth-oauthlib`, `jinja2`, `playwright`.
   Uzasadnienie:
   Pokrywają odpowiednio HTTP, parsowanie HTML, konfigurację środowiska, integrację z Google Sheets, renderowanie raportów HTML oraz automatyczne logowanie przeglądarkowe.
   Konsekwencje:
   Projekt wymaga poprawnej konfiguracji środowiska i jest zależny od zewnętrznych usług sieciowych.

7. Decyzja:
   Brak trwałych sekretów w repozytorium; konfiguracja przez zmienne środowiskowe oraz plik konta serwisowego poza repo.
   Uzasadnienie:
   Ogranicza ryzyko wycieku danych uwierzytelniających.
   Konsekwencje:
   Uruchomienie lokalne i produkcyjne wymaga starannego przygotowania środowiska oraz dokumentacji w `README.md`.

8. Decyzja (dotyczy PRD: `001-auto-cookie-login-prd.md`):
   Automatyczne logowanie do serwisu źródłowego będzie realizowane przez Playwright, a nie przez ręcznie odtwarzane żądania HTTP.
   Uzasadnienie:
   Playwright lepiej odwzorowuje rzeczywisty przebieg logowania, jest bardziej odporny na dynamiczny frontend i pozwala pobrać komplet aktualnych cookie po zalogowaniu.
   Konsekwencje:
   Projekt będzie wymagał dodatkowej zależności uruchomieniowej oraz obsługi środowiska przeglądarkowego.

9. Decyzja (dotyczy PRD: `001-auto-cookie-login-prd.md`):
   Istniejący przepływ pobierania stron pozostaje oparty na `requests.Session`, a Playwright pełni rolę pomocniczego komponentu uwierzytelnienia.
   Uzasadnienie:
   Pozwala to ograniczyć zakres zmian i zachować obecną logikę pobierania oraz parsowania stron.
   Konsekwencje:
   Potrzebne jest jawne mapowanie pełnego zestawu cookie z kontekstu Playwright do sesji HTTP, bo sam podzbiór cookie autoryzacyjnych nie wystarcza dla wszystkich stron.

10. Decyzja (dotyczy PRD: `001-auto-cookie-login-prd.md`):
    Dane logowania do serwisu źródłowego mają być przechowywane w zmiennych środowiskowych, a ręczne cookie mogą pozostać wyłącznie jako tryb awaryjny.
    Uzasadnienie:
    Spełnia to cel produktu polegający na usunięciu regularnej, ręcznej aktualizacji cookie, bez utraty ścieżki awaryjnej.
    Konsekwencje:
    README musi zostać rozszerzone o nowe zmienne środowiskowe i zasady ich użycia.

11. Decyzja (dotyczy PRD: `001-auto-cookie-login-prd.md`):
    Obsługa CAPTCHA i 2FA nie wchodzi do zakresu pierwszej wersji automatycznego logowania.
    Uzasadnienie:
    PRD zakłada standardowe logowanie formularzem login-hasło i ogranicza złożoność pierwszej iteracji.
    Konsekwencje:
    Jeśli serwis wymusi dodatkowe kroki uwierzytelnienia, konieczna będzie osobna decyzja produktowa i techniczna.

12. Decyzja (dotyczy PRD: `002-auth-retry-for-first-series-prd.md`):
    Wprowadzono ograniczony retry odzyskania sesji oraz ponowienie pobrania strony tego samego serialu po chwilowym błędzie logowania/cookie.
    Uzasadnienie:
    Obserwowane błędy mają charakter nieregularny, a pojedyncza nieudana próba logowania może fałszywie oznaczyć pierwszy serial na liście jako niedostępny.
    Konsekwencje:
    Czas pojedynczego przebiegu może wzrosnąć o czas dodatkowej próby, ale liczba fałszywych błędów dla pojedynczych seriali powinna spaść.

---

## Jakość i kryteria akceptacji
Wymagania jakościowe dla aktualnego stanu projektu:
- aplikację da się uruchomić jednym poleceniem przez `uv`
- pojedyncze uruchomienie kończy się kodem wyjścia odzwierciedlającym najpoważniejszy błąd spośród przetwarzanych użytkowników
- błędy dostępu do arkusza, parsowania i wysyłki są logowane
- aplikacja nie przechowuje sekretów bezpośrednio w repozytorium
- logowanie automatyczne odzyskuje sesję bez ręcznej aktualizacji cookie przez użytkownika

Luki jakościowe wymagające domknięcia w kolejnych pracach:
- brak formalnej walidacji konfiguracji wejściowej
- brak pełnej dokumentacji wszystkich wymaganych zmiennych środowiskowych w `README.md`
- brak smoke testu dla pełnego przebiegu z nowym mechanizmem sesji

Minimalne kryteria akceptacji dla bieżącej implementacji:
- dla poprawnej konfiguracji arkusza skrypt odczytuje dane bez błędu mapowania kolumn
- dla strony zawierającej odcinki skrypt potrafi wyznaczyć `latest_ready` oraz `max_found`
- gdy wykryto nowy odcinek, arkusz zostaje zaktualizowany, a e-mail zawiera pozycję na liście zmian
- gdy wystąpi błąd techniczny, trafia on do logów i do sekcji problemów w e-mailu, jeśli wysyłka jest możliwa

Minimalne kryteria akceptacji dla rozszerzenia z PRD `001-auto-cookie-login-prd.md`:
- dla poprawnych danych logowania aplikacja sama uzyskuje ważne cookie bez ręcznej ingerencji użytkownika
- cookie pozyskane przez Playwright mogą zostać użyte przez istniejący klient `requests.Session`
- pełny zestaw cookie z przeglądarki zachowuje dostęp także do stron wymagających dodatkowego stanu sesji, takich jak `City Hunter`
- po wygaśnięciu sesji aplikacja potrafi ponowić logowanie automatycznie
- błędy logowania są czytelnie raportowane i nie pozostają „ciche”

Minimalne kryteria akceptacji dla rozszerzenia z PRD `002-auth-retry-for-first-series-prd.md`:
- przy chwilowym błędzie odzyskania sesji aplikacja wykonuje dodatkową próbę logowania zamiast kończyć od razu błędem
- po udanym retry aplikacja ponawia sprawdzenie tego samego serialu i zwraca wynik bez błędu technicznego
- po wyczerpaniu limitu retry aplikacja raportuje błąd końcowy w sposób czytelny
- testy `unittest` obejmują scenariusz: pierwsza próba nieudana, druga udana

---

## Zasady zmian i ewolucji
- zmiany funkcjonalne → aktualizacja `ROADMAP.md`
- zmiany architektoniczne → aktualizacja tej specyfikacji
- nowe zależności → wpis do `## Decyzje techniczne`
- refactory tylko w ramach aktualnego milestone’u
- przy wydzielaniu modułów z `main.py` należy zachować jeden publiczny entrypoint opisany w `README.md`
- każda zmiana wymagająca nowych zmiennych środowiskowych musi być udokumentowana w `README.md`
- dodanie testów powinno używać `unittest` i stubów/fake’ów zamiast realnego IO

---

## Powiązanie z roadmapą
- Aktualna roadmapa w `ROADMAP.md` nie odzwierciedla faktycznego stanu implementacji, ponieważ projekt ma już działający przepływ wykraczający poza pusty szablon Milestone 0.5.
- Najbliższym zadaniem porządkującym powinno być urealnienie `ROADMAP.md` i `STATUS.md` względem obecnego kodu.
- Ta specyfikacja opisuje stan bieżącej implementacji, a nie docelowy, pełny plan rozwoju.
- PRD `001-auto-cookie-login-prd.md` został zrealizowany dla Milestone 1.0 i wprowadził automatyczne logowanie oraz odświeżanie sesji przez Playwright.
- PRD `002-auth-retry-for-first-series-prd.md` został zrealizowany i dodał odporność na chwilowe błędy logowania przez kontrolowane retry oraz ponowienie sprawdzenia serialu.

---

## Status specyfikacji
- Data utworzenia: 2026-03-21
- Ostatnia aktualizacja: 2026-03-23
- Aktualny zakres obowiązywania: bieżąca implementacja skryptu `main.py`, konfiguracja z `pyproject.toml`, opis projektu z `README.md`, wdrożone logowanie Playwright z PRD `001-auto-cookie-login-prd.md` oraz wdrożone retry autoryzacji z PRD `002-auth-retry-for-first-series-prd.md`
