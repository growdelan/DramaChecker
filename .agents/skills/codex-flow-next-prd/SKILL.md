---
name: codex-flow-next-prd
description: >
  Użyj, gdy w katalogu prd pojawia się kolejny przyrostowy PRD rozszerzający
  istniejący projekt i trzeba zaktualizować spec.md oraz ROADMAP.md bez zmiany
  kodu. W poleceniu użytkownika należy wskazać nazwę pliku PRD albo jednoznacznie
  wskazać, którego nowego PRD dotyczy aktualizacja. Nie używaj tego skilla do
  pierwszego bazowego PRD projektu.
---

Na podstawie wskazanego pliku `prd/<nazwa-pliku>.md`:

## ETAP 0 --- Ocena zmiany

0.1. Oceń zakres zmiany: **MAŁY / ŚREDNI / DUŻY**  
0.2. Oceń czy wpływa na istniejące milestone'y.  
0.3. Oceń czy istnieje potencjalny konflikt ze spec.  
0.4. Nie zapisuj tej oceny do plików.

---

## ETAP 1 --- Aktualizacja specyfikacji

1. Zaktualizuj `spec.md`, zachowując OBECNĄ strukturę.
2. Nie zmieniaj nagłówków ani kolejności sekcji.
3. Rozszerz tylko te sekcje, których dotyczy nowe PRD.
4. Nie usuwaj wcześniejszych decyzji.
5. Nowe decyzje techniczne dodaj do `## Decyzje techniczne` z oznaczeniem `(dotyczy PRD: nazwa-pliku)`.
6. Jeśli pojawia się konflikt:
   - opisz go w `## Decyzje techniczne`
   - nie rozwiązuj go samodzielnie
   - nie nadpisuj istniejących decyzji
7. Jeśli brakuje informacji, dodaj:

    TODO: [KONKRETNE PYTANIE DO DOPRECYZOWANIA]

---

## ETAP 2 --- Aktualizacja roadmapy

8. Zaktualizuj `ROADMAP.md`.
9. Nie zmieniaj istniejących milestone'ów ani ich statusów.
10. Nowe milestone'y dodaj na końcu z kolejną numeracją.
11. Każdy nowy milestone musi zawierać:

- Cel
- Definition of Done
- Zakres

12. Jeśli zakres = DUŻY:
- podziel implementację na mniejsze kroki
- dodaj milestone redukcji ryzyka

---

## ETAP 3 --- Spójność

13. Sprawdź:
- czy nowe milestone'y wynikają z aktualizacji spec
- czy nie powstały sprzeczności
- czy kolejność realizacji jest logiczna

---

## Zasady ogólne

- Jeśli użytkownik nie podał jednoznacznie nazwy pliku, wybierz najnowszy lub najbardziej oczywisty nowy plik z katalogu `prd/` i wskaż go w odpowiedzi.
- Nie zmieniaj struktury plików.
- Nie zmieniaj kodu.
- Nie zgaduj brakujących informacji.
- Generuj konkretne pytania zamiast domysłów.
