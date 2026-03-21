---
name: codex-flow-self-review
description: >
  Użyj po zakończeniu implementacji, gdy trzeba wykonać przegląd własnych
  ostatnich zmian pod kątem zgodności z ROADMAP.md, spec.md, AGENTS.md i
  jakości kodu. Najpierw przeanalizuj zmienione pliki, dokumentację i wyniki
  testów, a następnie przygotuj listę problemów oraz konkretnych poprawek.
  Nie wdrażaj jeszcze zmian. Nie używaj do implementacji funkcji ani do
  nanoszenia poprawek po review.
---

Wykonaj self-review ostatnich zmian.

Cel:
- sprawdzić spójność implementacji z dokumentacją projektu
- wykryć niespójności, naruszenia zasad i ryzyka jakościowe
- przygotować konkretną listę poprawek bez wprowadzania zmian w kodzie

Przebieg pracy:
1. Zidentyfikuj zakres ostatnich zmian:
   - sprawdź zmienione pliki
   - sprawdź, jaki milestone lub zadanie było realizowane
   - sprawdź, czy uruchomiono odpowiednie testy lub walidacje
2. Oceń zgodność z dokumentacją:
   - `ROADMAP.md`
   - `spec.md`
   - `AGENTS.md`
   - `README.md`, jeśli zmiany wpływają na sposób użycia lub uruchamiania
3. Oceń jakość wykonania:
   - poprawność rozwiązania
   - prostotę implementacji
   - duplikację logiki
   - zbędne abstrakcje
   - martwy kod
   - pokrycie testami i sensowność testów
4. Przygotuj wynik przeglądu.

Zasady:
- niczego jeszcze nie zmieniaj
- nie rozszerzaj zakresu review poza ostatnie zmiany, chyba że wykryjesz realny wpływ uboczny
- opieraj ocenę na faktycznym stanie repo i dokumentacji
- jeśli potrzebujesz bardziej szczegółowej checklisty lub formatu wyniku, użyj plików z `references/`
- jeśli potrzebujesz technicznego wsparcia do zebrania danych o zmianach lub uruchomienia walidacji, użyj skryptów z `scripts/`

Wynik:
- jeśli są problemy, wypisz je jasno i pogrupuj według ważności
- do każdego problemu dopisz proponowaną poprawkę
- jeśli wszystko jest poprawne, napisz dokładnie:
  `Self-review zakończony – brak problemów krytycznych.`
