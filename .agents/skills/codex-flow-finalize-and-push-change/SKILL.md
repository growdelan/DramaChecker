---
name: codex-flow-finalize-and-push-change
description: >
  Użyj po zakończeniu implementacji lub po wdrożeniu poprawek, gdy trzeba
  domknąć zmianę operacyjnie: zaktualizować ROADMAP.md, STATUS.md, a w razie
  potrzeby spec.md i README.md, następnie przygotować commit oraz wykonać push,
  jeśli repo ma skonfigurowany remote i stan jest gotowy do zapisania. Nie
  używaj do dodawania nowych funkcji ani planowania kolejnej pracy.
---

Domknij zmianę operacyjnie.

Przebieg pracy:
1. Sprawdź stan repo i zakres bieżącej zmiany.
2. Zaktualizuj dokumentację operacyjną:
   - `ROADMAP.md`
   - `STATUS.md`
   - `spec.md`, jeśli ostatnia praca zmieniła ustalenia lub decyzje techniczne
   - `README.md`, jeśli ostatnia praca zmieniła sposób użycia, uruchamiania, wymagania lub ważne zachowania systemu
3. Upewnij się, że dokumentacja odzwierciedla faktyczny stan repo.
4. Zweryfikuj, czy working tree jest gotowe do zapisania.
5. Przygotuj sensowny commit.
6. Wykonaj push tylko wtedy, gdy repo ma poprawnie skonfigurowany remote i nie ma sygnałów, że należy zatrzymać zmianę lokalnie.

Zasady:
- nie dodawaj nowej implementacji
- nie rozszerzaj zakresu pracy
- nie aktualizuj `README.md` ani `spec.md` kosmetycznie; zmieniaj je tylko wtedy, gdy stan repo realnie tego wymaga
- jeśli potrzebujesz doprecyzowania zasad aktualizacji dokumentacji lub commitowania, użyj plików z `references/`
- jeśli potrzebujesz sprawdzić stan working tree lub wykonać walidację przed pushem, użyj skryptów z `scripts/`

Wynik:
- podsumuj, które pliki dokumentacyjne zostały zaktualizowane
- podaj informację, czy wykonano commit
- podaj informację, czy wykonano push, czy świadomie go pominięto
