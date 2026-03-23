# PRD: Retry logowania i ponowienie sprawdzenia serialu po błędzie sesji

## Kontekst
Aktualnie aplikacja odzyskuje sesję dopiero wtedy, gdy przy próbie pobrania strony serialu wykryje brak autoryzacji.
W praktyce zdarza się błąd nieregularny:

- `Po logowaniu nie znaleziono wymaganych cookie sesyjnych.`

Błąd pojawia się najczęściej przy pierwszym serialu na liście (w bieżącej konfiguracji: `City Hunter`).

## Problem
Gdy jednorazowo nie powiedzie się krok odzyskania sesji (np. chwilowy problem po stronie logowania/cookie), dany serial dostaje błąd i nie jest ponawiany w tym samym przebiegu.

Skutek:
- fałszywy błąd dla serialu, mimo że kolejne próby w tej samej sesji lub chwilę później mogą przejść poprawnie
- wrażenie, że problem dotyczy konkretnego tytułu, podczas gdy przyczyna leży w niestabilności kroku logowania

## Cel
Zwiększyć odporność przepływu na chwilowe błędy autoryzacji przez kontrolowane retry.

Cel użytkowy:
- ograniczyć losowe błędy dla pierwszego serialu i zmniejszyć liczbę fałszywych alarmów

Cel techniczny:
- przy błędzie odzyskania sesji wykonać dodatkową próbę i dopiero potem zwrócić błąd końcowy

## Proponowane rozwiązanie
Wersja v1 retry:
1. Dla pojedynczego serialu utrzymać obecny przepływ detekcji braku autoryzacji.
2. Jeżeli pierwsza próba odzyskania sesji zakończy się błędem związanym z logowaniem/cookie, wykonać ponowną próbę odzyskania sesji.
3. Po udanym odzyskaniu sesji ponowić pobranie strony serialu.
4. Dopiero po wyczerpaniu retry zwrócić błąd do raportu.

Dodatkowo:
- dodać jednoznaczne logowanie numeru próby (attempt 1/2), aby odróżnić chwilową niestabilność od trwałej awarii

## Zakres v1
Do zakresu tej iteracji wchodzi:
- retry odzyskania sesji przy błędach logowania/cookie
- ponowienie sprawdzenia tego samego serialu po udanym odzyskaniu sesji
- ograniczenie liczby prób (mały, stały limit)
- czytelne logi diagnostyczne dla prób retry
- testy `unittest` pokrywające scenariusz: pierwsza próba logowania nieudana, druga udana

## Poza zakresem v1
Poza zakresem pozostają:
- trwały cache cookie w pliku między uruchomieniami
- przebudowa architektury `main.py` na wiele modułów
- zmiana dostawcy/technologii logowania
- obsługa CAPTCHA i 2FA

## Wymagania funkcjonalne
1. Przy chwilowym błędzie logowania/cookie aplikacja wykonuje co najmniej jedną dodatkową próbę odzyskania sesji.
2. Po udanym retry aplikacja ponawia pobranie strony tego samego serialu.
3. Jeśli retry się nie powiedzie, użytkownik dostaje błąd końcowy jak dotychczas, ale z pełniejszym kontekstem logów.
4. Retry nie może prowadzić do nieskończonej pętli.

## Wymagania niefunkcjonalne
- retry ma mieć stały, mały limit prób (deterministyczny czas wykonania)
- brak nowych sekretów i brak przechowywania sesji w repozytorium
- zgodność z uruchamianiem przez `uv`
- testy bez realnego IO (stuby/fake’i)

## Wpływ na istniejący system
- zmiana dotyczy wyłącznie ścieżki obsługi błędów autoryzacji
- główny model działania (Google Sheets -> requests -> parser -> e-mail) pozostaje bez zmian
- brak zmiany modelu konfiguracji środowiskowej w tej iteracji

## Kryteria sukcesu
Funkcjonalność będzie uznana za skuteczną, gdy:
- pojedyncza chwilowa awaria logowania nie kończy sprawdzania danego serialu błędem
- liczba losowych błędów podobnych do `Po logowaniu nie znaleziono wymaganych cookie sesyjnych` spada
- zachowanie przy trwałym błędzie logowania pozostaje czytelne i przewidywalne

## Kryteria akceptacji
1. Scenariusz testowy: pierwsza próba odzyskania sesji kończy się błędem, druga się udaje, serial jest poprawnie sprawdzony.
2. Scenariusz testowy: wszystkie próby odzyskania sesji nieudane, serial kończy się błędem końcowym.
3. W logach widoczna jest liczba wykonanych prób retry.
4. Brak regresji dla istniejących testów smoke.

## Ryzyka i ograniczenia
- retry może wydłużyć czas pojedynczego przebiegu
- jeśli problem jest trwały (np. zmiana formularza logowania), retry nie rozwiąże źródła problemu
- zbyt agresywny retry mógłby zwiększyć liczbę prób logowania; dlatego limit musi pozostać niski

## Założenia
- obecny błąd ma charakter nieregularny (intermittent), a nie permanentny
- druga próba logowania ma realną szansę powodzenia
- wdrożenie tej iteracji obejmuje dokumentację PRD; implementacja nastąpi w kolejnym kroku
