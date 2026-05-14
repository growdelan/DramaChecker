# PRD: Obsługa etykiet finałowych odcinków

## Kontekst
Parser odcinków został wcześniej zawężony tak, aby akceptować tylko etykiety dokładnie równe `Odcinek <numer>`. To wyeliminowało fałszywe wykrycia zapowiedzi i opisów informacyjnych, ale ujawniło zbyt restrykcyjne zachowanie dla finałów.

Potwierdzony przypadek produkcyjny:
- arkusz Google Sheets: serial `Climax` ma `odcinek_na_stronie=9` oraz `liczba_odcinków=10`
- strona: `https://www.dramaqueen.pl/drama/koreanska/climax/`
- aktualny label finału: `Odcinek 10 - Finał`
- obecny parser zwraca `latest_ready=9`, `max_found=9`, mimo że finał jest odblokowany i widoczny na stronie

## Problem
Finałowe odcinki bywają oznaczane dodatkowym dopiskiem `- Finał`, mimo że są realnie dostępne do oglądania.

W efekcie:
- arkusz może pozostać na przedostatnim dostępnym odcinku
- użytkownik nie dostaje powiadomienia o finale
- ręczne sprawdzenie strony jest nadal potrzebne dla części zakończonych seriali

## Cel
Rozszerzyć regułę parsowania o bezpieczny wyjątek dla polskich etykiet finałowych.

Cel użytkowy:
- finał serialu ma być wykrywany tak samo jak zwykły dostępny odcinek

Cel techniczny:
- parser ma akceptować `Odcinek <numer> - Finał`, ale nadal odrzucać zwykłe dopiski informacyjne, takie jak `Premiera w Korei: ...`

## Proponowane rozwiązanie
Wersja v1 fixu:
1. Zachować obecne wyszukiwanie kandydatów w elementach `p.toggler`.
2. Znormalizować tekst elementu tak jak obecnie, przez `get_text(" ", strip=True)`.
3. Uznawać element za odcinek, gdy cały tekst pasuje do jednego z formatów:
   - `Odcinek <numer>`
   - `Odcinek <numer> - Finał`
4. Dopuścić elastyczne spacje wokół myślnika oraz różną wielkość liter w słowie `Finał`.
5. Nie dopuszczać dowolnych sufiksów po myślniku ani angielskich wariantów `Final`/`Finale`.
6. Obecna reguła z obrazkiem blokady pozostaje bez zmiany:
   - element bez obrazka może podnosić `latest_ready`
   - element z obrazkiem może podnosić tylko `max_found`

Przykłady:
- poprawne: `Odcinek 10`
- poprawne: `Odcinek 10 - Finał`
- poprawne: `Odcinek 10-Finał`
- poprawne: `Odcinek 10 - finał`
- niepoprawne: `Odcinek 6 Premiera w Korei: 31.03.2026`
- niepoprawne: `Odcinek 6 - wkrótce`
- niepoprawne: `Odcinek 10 - Final`

## Zakres v1
Do zakresu tej iteracji wchodzi:
- rozszerzenie reguły wykrywania odcinków o polskie etykiety finałowe
- utrzymanie ochrony przed fałszywymi wykryciami dopisków informacyjnych
- utrzymanie obecnej logiki rozróżnienia między odcinkiem gotowym a zablokowanym przez obecność obrazka
- dodanie testów `unittest` dla etykiet finałowych i regresji `Climax`

## Poza zakresem v1
Poza zakresem pozostają:
- refaktoryzacja `main.py`
- zmiana selektorów HTML lub źródła danych
- obsługa dowolnych opisów po numerze odcinka
- obsługa angielskich albo innych językowych wariantów słowa `Finał`
- zmiany w logowaniu, Google Sheets, SMTP i konfiguracji środowiskowej

## Wymagania funkcjonalne
1. Element `Odcinek <numer> - Finał` ma być liczony jako odcinek.
2. Warianty spacji wokół myślnika i wielkości liter słowa `Finał` mają być akceptowane.
3. Element zawierający zwykły opis informacyjny nie może wpływać ani na `latest_ready`, ani na `max_found`.
4. Dla poprawnych prostych etykiet `Odcinek <numer>` obecne zachowanie ma pozostać bez zmiany.
5. Obecna detekcja zablokowanego odcinka przez obecność obrazka ma pozostać bez zmiany.

## Wymagania niefunkcjonalne
- brak nowych zależności
- brak zmian w konfiguracji środowiskowej
- testy bez realnego IO
- zgodność z obecnym uruchamianiem przez `uv`

## Wpływ na istniejący system
- zmiana dotyczy wyłącznie logiki parsowania HTML dla odcinków
- logowanie, Google Sheets, e-mail i mechanizm sesji pozostają bez zmian
- wynik parsowania pozostaje restrykcyjny, ale zawiera jawny wyjątek dla realnie dostępnych finałów

## Kryteria sukcesu
Funkcjonalność będzie uznana za skuteczną, gdy:
- `Odcinek 10 - Finał` będzie podnosił `latest_ready` do `10`, jeśli element nie ma obrazka blokady
- przypadek `Climax` przestanie zatrzymywać dostępny odcinek na wartości `9`
- dopiski typu `Premiera w Korei: ...` nadal będą ignorowane
- pełny zestaw testów `unittest` będzie przechodził lokalnie

## Kryteria akceptacji
1. Scenariusz: `Odcinek 10 - Finał` daje numer odcinka `10`.
2. Scenariusz: `Odcinek 10-Finał`, `Odcinek 10 - finał` i `Odcinek 10 - FINAŁ` są akceptowane.
3. Scenariusz: `Odcinek 6 Premiera w Korei: 31.03.2026` nadal jest ignorowany.
4. Scenariusz: HTML z `Odcinek 9` i odblokowanym `Odcinek 10 - Finał` daje `latest_ready=10`.
5. Scenariusz: HTML z `Odcinek 10 - Finał` z obrazkiem blokady nie podnosi `latest_ready`.

## Ryzyka i ograniczenia
- jeśli serwis zacznie oznaczać realnie dostępne odcinki innymi dopiskami niż `Finał`, parser nadal ich nie wykryje
- parser pozostaje zależny od struktury HTML serwisu
- rozwiązanie świadomie nie cofa ochrony wprowadzonej przez PRD `003-strict-episode-label-parsing-prd.md`

## Założenia
- obowiązującym formatem zwykłego odcinka pozostaje `Odcinek <numer>`
- jedynym dopuszczonym sufiksem w tej iteracji jest polskie `Finał`
- głównym kryterium biznesowym jest poprawne ustawienie dostępnego odcinka dla finału
