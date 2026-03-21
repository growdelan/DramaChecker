---
name: codex-flow-apply-self-review-fixes
description: >
  Użyj po wykonaniu self-review, gdy wykryto niespójności, naruszenia zasad lub
  problemy jakościowe i trzeba wdrożyć wyłącznie poprawki wynikające z tego
  przeglądu. Zachowaj zakres bieżącego milestone'u, nie dodawaj nowych funkcji
  i nie przebudowuj architektury bez wyraźnej potrzeby wynikającej z review.
  Po zakończeniu uruchom odpowiednie testy lub walidacje.
---

Zastosuj poprawki wynikające z self-review.

Cel:
- usunąć problemy wykryte podczas przeglądu
- przywrócić zgodność z dokumentacją i zasadami projektu
- poprawić jakość rozwiązania bez rozszerzania zakresu pracy

Przebieg pracy:
1. Przejrzyj wynik self-review i wybierz tylko poprawki rzeczywiście z niego wynikające.
2. Oceń każdą poprawkę pod kątem zakresu:
   - czy nadal mieści się w aktualnym milestone'ie
   - czy nie wprowadza nowej funkcjonalności
   - czy nie zmienia architektury bardziej, niż wymaga to problem
3. Wdróż poprawki.
4. Zaktualizuj testy lub dokumentację tylko wtedy, gdy jest to konieczne do domknięcia problemu.
5. Uruchom odpowiednie testy lub walidacje.
6. Podsumuj, jakie poprawki zostały wdrożone.

Zasady:
- nie zmieniaj zakresu milestone'u
- nie dodawaj nowych funkcjonalności
- nie wprowadzaj refaktoru wykraczającego poza potrzebę naprawy
- jeśli poprawka okazuje się nowym zakresem pracy, zatrzymaj ją i zaznacz to w podsumowaniu
- jeśli potrzebujesz doprecyzowania granicy zmian, użyj plików z `references/`
- jeśli potrzebujesz uruchomić zestaw walidacji po poprawkach, użyj skryptów z `scripts/`

Wynik:
- wypisz, które poprawki zostały wdrożone
- wskaż uruchomione testy lub walidacje
- zaznacz wszystko, czego świadomie nie wdrożono, bo wykraczało poza zakres self-review
