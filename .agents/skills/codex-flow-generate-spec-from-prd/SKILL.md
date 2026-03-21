---
name: codex-flow-generate-spec-from-prd
description: >
  Użyj, gdy w projekcie pojawia się pierwszy lub główny PRD, na podstawie którego
  trzeba wypełnić albo wygenerować zawartość spec.md i ROADMAP.md bez zmiany kodu.
  Wejściem jest bazowy plik PRD w katalogu prd, a wyjściem są spójne aktualizacje
  specyfikacji i roadmapy. Nie używaj tego skilla do kolejnych przyrostowych PRD,
  które tylko rozszerzają istniejący plan.
---

Na podstawie pliku `prd/000-initial-prd.md`:

## ETAP 0 --- Ocena zmiany

0.1. Oceń zakres PRD: **MAŁY / ŚREDNI / DUŻY**  
0.2. Oceń czy zawiera istotne ryzyka lub niejasności.  
0.3. Nie zapisuj tej oceny do plików --- użyj jej wyłącznie do
kalibracji roadmapy.

---

## ETAP 1 --- Specyfikacja

1. Wypełnij istniejący plik `spec.md`, korzystając z jego OBECNEJ struktury.
2. Nie zmieniaj nagłówków, nazw sekcji ani kolejności.
3. Uzupełnij sekcje na poziomie wysokim (bez szczegółów implementacyjnych).
4. Jeśli brakuje informacji, dodaj:

    TODO: [KONKRETNE PYTANIE DO DOPRECYZOWANIA]

5. Decyzje techniczne wpisuj wyłącznie do sekcji `## Decyzje techniczne` i tylko jeśli wynikają bezpośrednio z PRD.

---

## ETAP 2 --- Roadmapa

6. Wypełnij istniejący plik `ROADMAP.md`, zachowując jego strukturę.
7. Nie zmieniaj nazw sekcji ani dozwolonych statusów.
8. Zachowaj Milestone 0.5 jako pierwszy element.
9. Każdy milestone musi zawierać:
   - Cel
   - Definition of Done (mierzalne i testowalne)
   - Zakres
10. Jeśli zakres = DUŻY:
- rozbij implementację na mniejsze milestone'y
- dodaj milestone redukujący ryzyko (spike / walidacja)

---

## ETAP 3 --- Sprawdzenie spójności

11. Sprawdź:
- czy roadmapa wynika ze spec
- czy nie ma sprzeczności
- czy nie ma elementów w roadmapie, których nie ma w spec

---

## Zasady ogólne

- Nie zmieniaj struktury plików.
- Nie zmieniaj kodu.
- Nie zgaduj brakujących informacji.
- Generuj konkretne pytania zamiast domysłów.
