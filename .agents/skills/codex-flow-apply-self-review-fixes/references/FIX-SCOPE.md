# Granica zakresu poprawek po self-review

Dozwolone:
- dopisanie brakującego testu
- uproszczenie warunku lub przepływu sterowania
- usunięcie duplikacji ograniczonej do obszaru zmiany
- poprawa walidacji
- poprawa README lub dokumentacji operacyjnej, jeśli review wykazał braki
- mały refaktor konieczny do bezpiecznej naprawy problemu

Niedozwolone bez nowej decyzji planistycznej:
- dodawanie nowych ekranów, endpointów, funkcji i integracji
- przebudowa architektury, której review nie wymaga wprost
- szeroki refaktor niezwiązany bezpośrednio z wykrytym problemem
- "przy okazji" poprawianie innych obszarów repo
