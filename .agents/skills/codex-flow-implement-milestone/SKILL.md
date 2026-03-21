---
name: codex-flow-implement-milestone
description: >
  Użyj, gdy trzeba zaimplementować jeden konkretny milestone z ROADMAP.md inny
  niż Milestone 0.5. W poleceniu użytkownika należy wskazać identyfikator,
  nazwę albo jasno określić, który milestone ma zostać zrealizowany. Ten skill
  realizuje tylko zakres wskazanego milestone'u i nie służy do planowania,
  tworzenia roadmapy ani finalizacji całej zmiany.
---

Zaimplementuj wskazany milestone z `ROADMAP.md`.

Jeśli użytkownik nie podał jednoznacznie, który milestone ma być wdrożony:
- wybierz pierwszy milestone ze statusem `planned` lub `in_progress`, który nie jest Milestone 0.5
- krótko wskaż, który milestone został wybrany do realizacji

Zasady:
- realizuj wyłącznie zakres danego milestone’u
- nie zmieniaj architektury bez wyraźnej potrzeby
- jeśli zakres jest niejasny:
  - najpierw doprecyzuj `ROADMAP.md` lub `spec.md`
  - dopiero potem implementuj

Po zakończeniu:
- uruchom testy
