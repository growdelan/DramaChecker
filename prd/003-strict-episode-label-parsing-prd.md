# PRD: Ścisłe wykrywanie odcinków bez dodatkowych opisów

## Kontekst
Aktualnie parser odcinków uznaje element strony za odcinek, jeśli jego tekst zawiera wzorzec `Odcinek <numer>`.
To podejście jest zbyt szerokie, ponieważ niektóre labelki zawierają numer odcinka oraz dodatkowy opis informacyjny, mimo że odcinek nie jest jeszcze realnie dostępny do oglądania.

Potwierdzony przypadek produkcyjny:
- strona: `https://www.dramaqueen.pl/drama/koreanska/climax/`
- aktualny label: `Odcinek 6 Premiera w Korei: 31.03.2026`
- obecny parser błędnie uznaje ten element za istniejący odcinek i zwraca `latest_ready=6`, `max_found=6`

## Problem
Nie wszystkie labelki z numerem odcinka oznaczają realnie istniejący odcinek na stronie.

W efekcie:
- arkusz może zostać zaktualizowany zbyt wcześnie
- użytkownik dostaje fałszywe powiadomienia o nowych odcinkach
- stan obejrzenia zaczyna rozjeżdżać się z rzeczywistą dostępnością odcinków

## Cel
Zawęzić regułę parsowania tak, aby za istniejące były uznawane wyłącznie te odcinki, których label po normalizacji jest dokładnie równy `Odcinek <numer>`.

Cel użytkowy:
- użytkownik ma dostawać tylko realnie dostępne odcinki, bez zapowiedzi i etykiet informacyjnych

Cel techniczny:
- parser ma odrzucać elementy, które zawierają dodatkowy opis poza samym `Odcinek <numer>`

## Proponowane rozwiązanie
Wersja v1 fixu:
1. Zachować obecne wyszukiwanie kandydatów w elementach `p.toggler`.
2. Znormalizować tekst elementu tak jak obecnie, przez `get_text(" ", strip=True)`.
3. Uznawać element za odcinek tylko wtedy, gdy cały znormalizowany tekst pasuje dokładnie do wzorca `Odcinek <numer>`.
4. Elementy z dodatkowym tekstem mają zostać odrzucone, nawet jeśli zawierają numer odcinka.
5. Obecna reguła z obrazkiem blokady pozostaje bez zmiany:
   - element bez obrazka może podnosić `latest_ready`
   - element z obrazkiem może podnosić tylko `max_found`

Przykłady:
- poprawne: `Odcinek 5`
- niepoprawne: `Odcinek 6 Premiera w Korei: 31.03.2026`
- niepoprawne: `Odcinek 6 - wkrótce`
- niepoprawne: `Odcinek 6 Napisy wkrótce`

## Zakres v1
Do zakresu tej iteracji wchodzi:
- doprecyzowanie reguły wykrywania odcinków do pełnego dopasowania całego labela
- odrzucanie etykiet z dodatkowymi opisami, nawet jeśli zawierają numer odcinka
- utrzymanie obecnej logiki rozróżnienia między odcinkiem gotowym a zablokowanym przez obecność obrazka
- dodanie testów `unittest` dla etykiet z dodatkowymi dopiskami

## Poza zakresem v1
Poza zakresem pozostają:
- refaktoryzacja `main.py`
- zmiana selektorów HTML lub źródła danych
- próba interpretowania innych opisów jako stanów pośrednich
- heurystyki dla innych formatów niż dokładne `Odcinek <numer>`

## Wymagania funkcjonalne
1. Element ma być liczony jako odcinek tylko wtedy, gdy cały jego tekst jest dokładnie równy `Odcinek <numer>`.
2. Element zawierający dodatkowy tekst nie może wpływać ani na `latest_ready`, ani na `max_found`.
3. Dla poprawnych prostych etykiet obecne zachowanie ma pozostać bez zmiany.
4. Obecna detekcja zablokowanego odcinka przez obecność obrazka ma pozostać bez zmiany.

## Wymagania niefunkcjonalne
- brak nowych zależności
- brak zmian w konfiguracji środowiskowej
- testy bez realnego IO
- zgodność z obecnym uruchamianiem przez `uv`

## Wpływ na istniejący system
- zmiana dotyczy wyłącznie logiki parsowania HTML dla odcinków
- logowanie, Google Sheets, e-mail i mechanizm sesji pozostają bez zmian
- wynik parsowania ma być bardziej zachowawczy i bliższy rzeczywistej dostępności odcinków

## Kryteria sukcesu
Funkcjonalność będzie uznana za skuteczną, gdy:
- labelki z dodatkowymi dopiskami nie będą już podnosić numeru wykrytego odcinka
- przypadek `Climax` przestanie fałszywie wykrywać odcinek 6 jako dostępny
- proste przypadki `Odcinek <numer>` dalej będą parsowane poprawnie

## Kryteria akceptacji
1. Scenariusz: `Odcinek 1`, `Odcinek 2`, `Odcinek 3` z obrazkiem blokady daje `latest_ready=2`, `max_found=3`.
2. Scenariusz: `Odcinek 6 Premiera w Korei: 31.03.2026` jest ignorowany i nie podnosi żadnego wyniku.
3. Scenariusz mieszany: `Odcinek 5`, `Odcinek 6 Premiera w Korei: 31.03.2026`, `Odcinek 7` z obrazkiem blokady daje `latest_ready=5`, `max_found=7`.
4. Scenariusz bez żadnego dokładnego labela `Odcinek <numer>` nadal kończy się błędem `Nie znaleziono nagłówków odcinków.`

## Ryzyka i ograniczenia
- jeśli serwis zacznie oznaczać realnie dostępne odcinki dodatkowymi dopiskami, nowa reguła może stać się zbyt restrykcyjna
- parser nadal pozostaje zależny od struktury HTML serwisu
- rozwiązanie świadomie preferuje fałszywy brak odcinka zamiast fałszywego wykrycia odcinka

## Założenia
- obowiązującym formatem realnie dostępnego odcinka jest dokładnie `Odcinek <numer>`
- dodatkowy tekst w tym samym labelu oznacza informację pomocniczą, zapowiedź albo inny stan niż realna dostępność
- wdrożenie tej iteracji obejmuje dokumentację PRD; implementacja nastąpi w kolejnym kroku
