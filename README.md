# DramaChecker

Skrypt sprawdzający nowe odcinki K-dram w arkuszu Google Sheets i wysyłający powiadomienia e-mail.

## Konfiguracja wielu użytkowników

Program może obsłużyć wielu użytkowników. Utwórz plik JSON z listą konfiguracji, np. `users.json`:

```json
[
  {
    "sheet_title": "dramy-ania",
    "worksheet_title": "arkusz1",
    "email_to": "ania@example.com"
  },
  {
    "sheet_title": "dramy-basia",
    "worksheet_title": "arkusz1",
    "email_to": "basia@example.com"
  }
]
```

Ścieżkę do pliku podaj w zmiennej środowiskowej `USERS_CONFIG`. Każdy wpis może dodatkowo zawierać pola `service_account_file` oraz `always_send`.

Gdy `USERS_CONFIG` nie jest ustawione, skrypt korzysta z dotychczasowych zmiennych (`SHEET_TITLE`, `WORKSHEET_TITLE`, `EMAIL_TO` itd.) i działa dla jednego użytkownika.