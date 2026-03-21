# AGENTS.md

Ten plik jest wyłącznie operacyjny: jak uruchamiać, testować i zarządzać zależnościami.
Decyzje produktowe/architektura: `spec.md` / `ROADMAP.md` / `STATUS.md`.

## Język
- Komunikacja wyłącznie po polsku.

## Środowisko i zależności
- Używaj `uv` do zarządzania środowiskiem i zależnościami (nie twórz innych venv).
- Dodawanie zależności: `uv add <pakiet>`.
- Każda nowa zależność musi być uzasadniona w `spec.md` (sekcja „Decyzje techniczne”).

## Uruchamianie
- Preferuj uruchamianie przez `uv`:
  - `uv run python -m <moduł_lub_pakiet>`
- Alternatywnie (pojedynczy plik):
  - `uv run <plik.py>`
- Komenda uruchomienia musi być opisana w `README.md`.

## Testy
- Framework: `unittest`.
- Uruchomienie:
  - `uv run python -m unittest discover -s tests -p "test_*.py"`
- Smoke testy: bez IO (sieć/API/dysk); używaj stubów/fake’ów.

## Konwencje repo
- Kod w `src/` (albo w root tylko dla małych projektów); testy w `tests/`.
- Nie dodawaj dodatkowych `.py` do root’a, jeśli używasz struktury `src/`.
- Jeden entrypoint, opisany w `README.md`.

## Sekrety i konfiguracja
- Nie przechowuj sekretów w repo.
- Używaj zmiennych środowiskowych i dokumentuj je w `README.md`.
- Bez domyślnych kluczy i fallbacków.

## Styl
- Indentacja: 4 spacje.
- Nazwy: moduły/funkcje `snake_case`, klasy `PascalCase`.
- Kod prosty, bez „magii”; komentarze tylko przy nieoczywistej logice.

