# DramaChecker

Skrypt sprawdzający nowe odcinki K-dram w arkuszu Google Sheets i wysyłający powiadomienia e-mail.

Obsługuje automatyczne logowanie do DramaQueen przez Playwright, więc nie trzeba już ręcznie odnawiać cookie w `.env`.

## Uruchamianie

Preferowana komenda:

```bash
uv run python main.py
```

Przed pierwszym użyciem logowania przez Playwright zainstaluj przeglądarkę:

```bash
uv run playwright install chromium
```

## Konfiguracja wielu użytkowników

Repo zawiera bezpieczny przykład konfiguracji w pliku `users.example.json`.

Skopiuj go lokalnie do własnego `users.json` i uzupełnij prawdziwymi danymi:

```bash
cp users.example.json users.json
```

Program może obsłużyć wielu użytkowników. Przykładowa zawartość:

```json
[
  {
    "sheet_title": "example-dramy",
    "worksheet_title": "Arkusz1",
    "email_to": "example@example.com"
  }
]
```

Ścieżkę do pliku podaj w zmiennej środowiskowej `USERS_CONFIG`. Każdy wpis może dodatkowo zawierać pola `service_account_file` oraz `always_send`.

Gdy `USERS_CONFIG` nie jest ustawione, skrypt korzysta z dotychczasowych zmiennych (`SHEET_TITLE`, `WORKSHEET_TITLE`, `EMAIL_TO` itd.) i działa dla jednego użytkownika.

Prawdziwy `users.json` pozostaje lokalny i nie powinien trafiać do repo.

## Wymagane zmienne środowiskowe

Minimalnie:
- `GSPREAD_SERVICE_ACCOUNT_FILE`
- `EMAIL_TO` albo `USERS_CONFIG`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASS`
- `EMAIL_FROM`

Do automatycznego logowania:
- `DRAMAQUEEN_USERNAME`
- `DRAMAQUEEN_PASSWORD`

Opcjonalne ustawienia logowania Playwright:
- `DRAMAQUEEN_LOGIN_URL`
- `DRAMAQUEEN_AUTH_DOMAIN`
- `DRAMAQUEEN_LOGIN_USERNAME_SELECTOR`
- `DRAMAQUEEN_LOGIN_PASSWORD_SELECTOR`
- `DRAMAQUEEN_LOGIN_SUBMIT_SELECTOR`
- `DRAMAQUEEN_LOGIN_SUCCESS_URL_CONTAINS`
- `DRAMAQUEEN_LOGIN_HEADLESS`
- `DRAMAQUEEN_LOGIN_TIMEOUT_MS`

Ręczne cookie mogą nadal działać jako fallback awaryjny:
- `PHPSESSID`
- `WP_LOGGED_IN_COOKIE_NAME`
- `WP_LOGGED_IN_COOKIE_VALUE`
- `WP_SEC_COOKIE_NAME`
- `WP_SEC_COOKIE_VALUE`

## Testy

```bash
uv run python -m unittest discover -s tests -p "test_*.py"
```
