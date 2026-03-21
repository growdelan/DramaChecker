# PRD: Automatyczne logowanie i odświeżanie cookie przez Playwright

## Kontekst
Obecnie DramaChecker wymaga ręcznego wpisywania do `.env` wartości cookie potrzebnych do dostępu do serwisu źródłowego. Te wartości wygasają cyklicznie, w praktyce co kilka dni, przez co użytkownik musi regularnie odświeżać je ręcznie.

To powoduje:
- przerywanie działania automatyzacji
- dodatkową pracę operacyjną po stronie użytkownika
- większe ryzyko błędów konfiguracyjnych
- zależność od ręcznego utrzymywania sesji

## Problem
Użytkownik chce, aby aplikacja sama logowała się do serwisu i sama utrzymywała ważną sesję, bez konieczności ręcznego przepisywania cookie do `.env`.

Obecny model oparty na ręcznych wartościach `PHPSESSID` i pokrewnych cookie nie spełnia tego celu, bo:
- sesja wygasa
- odnowienie wymaga ręcznej ingerencji
- rozwiązanie nie skaluje się operacyjnie

## Cel
Dodać funkcjonalność, która pozwoli aplikacji:
- samodzielnie zalogować się do serwisu źródłowego
- pobrać aktualne cookie po zalogowaniu
- używać tych cookie w istniejącym przepływie sprawdzania odcinków
- automatycznie odzyskiwać sesję po jej wygaśnięciu

Cel użytkowy:
- użytkownik nie musi już ręcznie aktualizować cookie w `.env`

Cel techniczny:
- aplikacja uzyskuje i odnawia ważną sesję samodzielnie, przy zachowaniu obecnego modelu pracy opartego na `requests.Session`

## Proponowane rozwiązanie
Wersja v1 ma wykorzystywać Playwright jako mechanizm automatycznego logowania.

Proponowany przepływ:
1. Aplikacja sprawdza, czy ma ważną sesję do serwisu źródłowego.
2. Jeśli sesja jest ważna, używa aktualnych cookie do pobierania stron seriali.
3. Jeśli sesja jest nieważna albo brak oznak zalogowania, aplikacja uruchamia Playwright.
4. Playwright otwiera stronę logowania, wypełnia formularz loginem i hasłem z konfiguracji środowiskowej oraz wykonuje logowanie.
5. Po poprawnym zalogowaniu aplikacja odczytuje cookie z kontekstu przeglądarki.
6. Cookie są mapowane do istniejącej sesji HTTP używanej przez aplikację.
7. Dalsze pobieranie stron odbywa się już przez obecny klient `requests.Session`.
8. Przy ponownej utracie autoryzacji proces logowania jest wykonywany ponownie automatycznie.

## Dlaczego Playwright
Playwright jest wybranym rozwiązaniem dla v1, ponieważ:
- wykonuje prawdziwe logowanie w przeglądarce i lepiej odwzorowuje rzeczywistą sesję użytkownika
- jest bardziej odporny na dynamiczny frontend i ukryte zależności formularza logowania niż podejście oparte wyłącznie na `requests`
- pozwala w prosty sposób odczytać komplet cookie po zakończonym logowaniu
- daje większą trwałość rozwiązania niż ręcznie odtwarzane żądania HTTP

Podejście oparte wyłącznie na `requests` nie jest wybierane jako kierunek v1, ponieważ byłoby bardziej kruche i silniej zależne od szczegółów implementacji formularza logowania po stronie serwisu.

## Zakres v1
Do zakresu pierwszej wersji wchodzi:
- logowanie do serwisu loginem i hasłem przez Playwright
- pobranie aktualnych cookie po zalogowaniu
- przekazanie cookie do istniejącej sesji `requests.Session`
- wykrywanie utraty autoryzacji
- automatyczne ponowne logowanie po wygaśnięciu sesji
- raportowanie błędów logowania w sposób czytelny dla użytkownika i logów aplikacji

## Poza zakresem v1
Poza zakresem tej iteracji pozostają:
- obsługa CAPTCHA
- obsługa 2FA
- obsługa wielu niezależnych kont logowania do serwisu
- interaktywny panel zarządzania sesją
- ręczne sterowanie przeglądarką przez użytkownika
- pełne przejście całej aplikacji z `requests` na Playwright

## Wymagania funkcjonalne
1. Aplikacja ma umożliwiać zalogowanie do serwisu bez ręcznego dostarczania cookie do `.env`.
2. Aplikacja ma używać cookie pozyskanych przez Playwright w obecnym przepływie pobierania stron.
3. Aplikacja ma wykrywać utratę ważnej sesji i wykonywać ponowne logowanie automatycznie.
4. Aplikacja ma raportować nieudane logowanie w logach i w istniejącym mechanizmie raportowania błędów.
5. Ręczne cookie mogą pozostać jako tryb awaryjny, ale nie mogą być już podstawowym sposobem działania.

## Wymagania niefunkcjonalne
- sekrety logowania nie mogą być przechowywane w repozytorium
- logowanie ma być wykonywane tylko wtedy, gdy jest potrzebne
- rozwiązanie ma ograniczać liczbę zbędnych uruchomień przeglądarki
- mechanizm ma być odporny na typowe wygaśnięcie sesji
- rozwiązanie ma być możliwe do uruchamiania z obecnego środowiska projektu

## Zmiany w konfiguracji
W ramach późniejszej implementacji należy dodać konfigurację środowiskową dla:
- loginu do serwisu
- hasła do serwisu
- ewentualnych ustawień wykonania Playwright, jeśli okażą się potrzebne operacyjnie

Docelowy model konfiguracji:
- dane logowania są przechowywane w zmiennych środowiskowych
- cookie nie są już podstawową daną wejściową zarządzaną ręcznie przez użytkownika

## Wpływ na istniejący system
Planowana funkcjonalność ma rozszerzyć obecny system, a nie zastąpić cały mechanizm pobierania danych.

Zakładany wpływ:
- warstwa pobierania stron nadal korzysta z `requests.Session`
- pojawia się dodatkowy komponent odpowiedzialny za uzyskanie i odświeżenie sesji
- logika uwierzytelnienia staje się osobnym elementem odpowiedzialności

## Kryteria sukcesu
Funkcjonalność będzie uznana za spełniającą cel, gdy:
- użytkownik nie musi ręcznie aktualizować cookie w `.env`
- aplikacja potrafi sama uzyskać ważną sesję po starcie
- aplikacja potrafi sama odzyskać sesję po jej wygaśnięciu
- obecny przepływ sprawdzania odcinków działa dalej po przejęciu zarządzania sesją przez nowy mechanizm

## Kryteria akceptacji
1. Przy poprawnych danych logowania aplikacja uzyskuje ważne cookie bez ręcznej ingerencji użytkownika.
2. Uzyskane cookie mogą zostać użyte do pobrania stron wymagających zalogowanej sesji.
3. Gdy sesja wygaśnie, aplikacja ponawia logowanie automatycznie.
4. Gdy logowanie się nie powiedzie, użytkownik dostaje czytelną informację o błędzie.
5. Wdrożenie v1 nie zakłada obsługi CAPTCHA ani 2FA.

## Ryzyka i ograniczenia
- zmiana formularza logowania lub struktury strony może wymagać aktualizacji selektorów Playwright
- serwis może w przyszłości dodać CAPTCHA lub 2FA, co wykracza poza zakres v1
- uruchamianie Playwright zwiększy złożoność środowiska wykonawczego względem obecnego skryptu

## Założenia
- serwis źródłowy pozwala na standardowe logowanie formularzem login i hasło
- logowanie nie wymaga obowiązkowego 2FA
- logowanie nie wymaga stałej CAPTCHA
- w kolejnej iteracji dopuszczalne będzie dodanie Playwright jako zależności projektu
- implementacja tej funkcjonalności nie wymaga w tym kroku zmian w kodzie, a jedynie przygotowania dokumentu produktowego
