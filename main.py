#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import re
import sys
import logging
import smtplib
from email.message import EmailMessage
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import gspread
from gspread.exceptions import APIError, SpreadsheetNotFound, WorksheetNotFound

# ------------------------------------------------------------
# Konfiguracja logowania
# ------------------------------------------------------------
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# Stałe & regexy
# ------------------------------------------------------------
EPISODE_RE = re.compile(r"Odcinek\s*(\d+)", re.IGNORECASE)
# Dodatkowo obsłużymy możliwe formaty z myślnikiem, np. "Odcinek 20 - Finał"
EPISODE_ANY_RE = re.compile(r"Odcinek\s*(\d+)")

# Nagłówki użytkownika
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

# Domyślne nazwy kolumn (wraz z tolerancją literówki)
COLUMN_ALIASES = {
    "nazwa": ["nazwa", "tytuł", "tytul"],
    "link": ["link", "url"],
    "obejrzany_odcinek": ["obejrzany_odcinek", "last_watched", "obejrzany"],
    "odcinek_na_stronie": ["odcinek_na_stronie", "last_on_site", "na_stronie"],
    "liczba_odcinków": ["liczba_odcinków", "liczba_odicnków", "liczba_odc", "max_odcinek"],
}

@dataclass
class SeriesRow:
    row_idx: int  # 1-based index w arkuszu (włącznie z nagłówkiem)
    nazwa: str
    link: str
    obejrzany_odcinek: int
    odcinek_na_stronie: int
    liczba_odcinków: int

    @property
    def is_done(self) -> bool:
        return (
            self.obejrzany_odcinek == self.odcinek_na_stronie == self.liczba_odcinków
        )

@dataclass
class EpisodeCheckResult:
    latest_ready: Optional[int]  # najnowszy gotowy (bez <img> w nagłówku)
    max_found: Optional[int]     # najwyższy numer odcinka znaleziony na stronie (niezależnie od <img>)
    error: Optional[str] = None

# ------------------------------------------------------------
# Utilsy
# ------------------------------------------------------------

def getenv_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except Exception:
        return default


def parse_int(value: object, default: int = 0) -> int:
    try:
        if isinstance(value, (int, float)):
            return int(value)
        if value is None:
            return default
        s = str(value).strip()
        if not s:
            return default
        return int(re.sub(r"\D", "", s))
    except Exception:
        return default


# ------------------------------------------------------------
# Parsowanie HTML – logika odcinków
# ------------------------------------------------------------

def extract_episode_number(text: str) -> Optional[int]:
    match = EPISODE_ANY_RE.search(text)
    if match:
        try:
            return int(match.group(1))
        except Exception:
            return None
    return None


def find_episodes(html: str) -> EpisodeCheckResult:
    """Zwraca najnowszy gotowy odcinek (bez <img> w p.toggler) i max numer odcinka.
    W razie problemu ustawia error.
    """
    try:
        soup = BeautifulSoup(html, "html.parser")
        p_tags = soup.find_all("p", class_=lambda c: c and "toggler" in c)
        latest_ready = None
        max_found = None

        for p in p_tags:
            text = p.get_text(" ", strip=True)
            num = extract_episode_number(text)
            if num is not None:
                if max_found is None or num > max_found:
                    max_found = num
            # jeżeli w nagłówku jest <img> – to jest korekta/tłumaczenie => NIE gotowy
            has_img = p.find("img") is not None
            if not has_img and num is not None:
                if latest_ready is None or num > latest_ready:
                    latest_ready = num

        if latest_ready is None and max_found is None:
            return EpisodeCheckResult(None, None, error="Nie znaleziono żadnego nagłówka odcinka.")
        return EpisodeCheckResult(latest_ready, max_found, None)
    except Exception as e:
        return EpisodeCheckResult(None, None, error=f"Błąd parsowania HTML: {e}")


# ------------------------------------------------------------
# Dostęp do Google Sheets
# ------------------------------------------------------------

def authenticate_gspread(service_account_file: str) -> gspread.Client:
    # Zalecana autoryzacja przez konto serwisowe
    return gspread.service_account(filename=service_account_file)


def open_sheet(gc: gspread.Client, spreadsheet_title: str, worksheet_title: str):
    # Otwieramy arkusz przez tytuł – alternatywnie można użyć ID (bezpieczniej)
    try:
        sh = gc.open(spreadsheet_title)
    except SpreadsheetNotFound as e:
        raise RuntimeError(
            "Nie znaleziono arkusza. Upewnij się, że udostępniłeś arkusz na adres 'client_email' z pliku service_account.json."
        ) from e

    try:
        ws = sh.worksheet(worksheet_title)
    except WorksheetNotFound as e:
        # Fallback: weź pierwszy
        ws = sh.sheet1
        logger.warning(
            "Nie znaleziono zakładki '%s'. Używam pierwszej zakładki: %s",
            worksheet_title, ws.title,
        )
    return sh, ws


def map_headers(header_row: List[str]) -> Dict[str, int]:
    """Zwraca mapowanie 'kanoniczna_nazwa' -> index kolumny (0-based)."""
    header_norm = [str(h or "").strip().lower() for h in header_row]
    mapping: Dict[str, int] = {}
    for canon, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in header_norm:
                mapping[canon] = header_norm.index(alias)
                break
    missing = [k for k in ("nazwa", "link", "obejrzany_odcinek", "odcinek_na_stronie", "liczba_odcinków") if k not in mapping]
    if missing:
        raise RuntimeError(f"Brak wymaganych kolumn w nagłówku: {missing}. Otrzymano: {header_row}")
    return mapping


def read_series(ws) -> Tuple[List[SeriesRow], List[str], Dict[str, int]]:
    """Wczytuje wszystkie wiersze i mapuje na SeriesRow."""
    values = ws.get_all_values()  # 2D list
    if not values:
        raise RuntimeError("Arkusz jest pusty.")
    header = values[0]
    mapping = map_headers(header)

    rows: List[SeriesRow] = []
    for i, row in enumerate(values[1:], start=2):  # 1=header, więc dane od 2
        def get(idx: int) -> str:
            return row[idx] if idx < len(row) else ""

        s = SeriesRow(
            row_idx=i,
            nazwa=get(mapping["nazwa"]),
            link=get(mapping["link"]),
            obejrzany_odcinek=parse_int(get(mapping["obejrzany_odcinek"]), 0),
            odcinek_na_stronie=parse_int(get(mapping["odcinek_na_stronie"]), 0),
            liczba_odcinków=parse_int(get(mapping["liczba_odcinków"]), 0),
        )
        rows.append(s)
    return rows, header, mapping


def update_cell(ws, row_idx: int, col_idx: int, value: object):
    # gspread jest 1-based
    ws.update_cell(row_idx, col_idx, value)


# ------------------------------------------------------------
# Email
# ------------------------------------------------------------

def build_email_body(new_items: List[dict], problems: List[str]) -> str:
    lines: List[str] = []
    if new_items:
        lines.append("Nowe odcinki do obejrzenia:\n")
        for i, it in enumerate(new_items, start=1):
            lines.append(f"{i}. Tytuł: {it['tytuł']}")
            lines.append(f"   Nowy odcinek: {it['nowy_odcinek']}")
            lines.append(f"   Ostatni obejrzany: {it['ostatni_obejrzany']}")
            lines.append(f"   Link: {it['link']}\n")
    else:
        lines.append("Brak nowych odcinków do obejrzenia.\n")

    if problems:
        lines.append("Problemy techniczne:")
        for p in problems:
            lines.append(f"- {p}")
    else:
        lines.append("Problemy techniczne: brak")

    return "\n".join(lines)


def send_email(subject: str, body: str) -> None:
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = getenv_int("SMTP_PORT", 587)
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    email_to = os.environ.get("EMAIL_TO")
    email_from = os.environ.get("EMAIL_FROM", smtp_user)

    if not (smtp_user and smtp_pass and email_to):
        raise RuntimeError("Brak ustawień SMTP/EMAIL_TO w .env")

    msg = EmailMessage()
    msg["From"] = email_from
    msg["To"] = email_to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=60) as server:
        server.ehlo()
        # STARTTLS jeśli port 587
        if smtp_port == 587:
            server.starttls()
            server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        logger.info("Wysłano e-mail do %s", email_to)


# ------------------------------------------------------------
# Główna logika
# ------------------------------------------------------------

def build_requests_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": DEFAULT_USER_AGENT})

    # Ciasteczka WordPress / DramaQueen – nazwy mogą się różnić; pobierz z .env
    php_sessid = os.environ.get("PHPSESSID")
    if php_sessid:
        s.cookies.set("PHPSESSID", php_sessid, domain="www.dramaqueen.pl")

    # Dwa inne ciastka mogą mieć zmienny suffix; przekaż nazwę i wartość
    wp_logged_in_name = os.environ.get("WP_LOGGED_IN_COOKIE_NAME")
    wp_logged_in_val = os.environ.get("WP_LOGGED_IN_COOKIE_VALUE")
    if wp_logged_in_name and wp_logged_in_val:
        s.cookies.set(wp_logged_in_name, wp_logged_in_val, domain="www.dramaqueen.pl")

    wp_sec_name = os.environ.get("WP_SEC_COOKIE_NAME")
    wp_sec_val = os.environ.get("WP_SEC_COOKIE_VALUE")
    if wp_sec_name and wp_sec_val:
        s.cookies.set(wp_sec_name, wp_sec_val, domain="www.dramaqueen.pl")

    return s


def check_series(session: requests.Session, series: SeriesRow) -> EpisodeCheckResult:
    try:
        resp = session.get(series.link, timeout=60)
        if resp.status_code != 200:
            return EpisodeCheckResult(None, None, error=f"{series.nazwa}: HTTP {resp.status_code}")
        return find_episodes(resp.text)
    except Exception as e:
        return EpisodeCheckResult(None, None, error=f"{series.nazwa}: błąd pobierania: {e}")


def main() -> int:
    load_dotenv()

    spreadsheet_title = os.environ.get("SHEET_TITLE", "dramy")
    worksheet_title = os.environ.get("WORKSHEET_TITLE", "arkusz1")
    service_account_file = os.environ.get("GSPREAD_SERVICE_ACCOUNT_FILE", "service_account.json")

    always_send = os.environ.get("ALWAYS_SEND", "1") in ("1", "true", "True", "yes", "tak")

    # 1. GSheets – wczytaj dane
    try:
        gc = authenticate_gspread(service_account_file)
        sh, ws = open_sheet(gc, spreadsheet_title, worksheet_title)
        rows, header, mapping = read_series(ws)
        logger.info("Wczytano %d wierszy z arkusza '%s/%s'", len(rows), spreadsheet_title, ws.title)
    except Exception as e:
        logger.exception("Błąd dostępu do Google Sheets: %s", e)
        # Jeśli nawet Sheets padnie – wyślij e-mail z informacją o błędzie
        try:
            send_email("Sprawdzacz odcinków – błąd Sheets", f"Błąd dostępu do Google Sheets: {e}")
        except Exception:
            pass
        return 2

    # 2. HTTP session z ciasteczkami
    session = build_requests_session()

    new_items: List[dict] = []
    problems: List[str] = []

    # 3. Iteracja po wierszach
    for s in rows:
        # Pomiń kompletne (obejrzany == na_stronie == liczba)
        if s.is_done:
            logger.debug("Pomijam kompletne: %s", s.nazwa)
            continue

        if not s.link:
            problems.append(f"{s.nazwa}: brak linku w arkuszu")
            continue

        result = check_series(session, s)
        if result.error:
            problems.append(result.error)
            continue

        latest_ready = result.latest_ready or 0
        max_found = result.max_found or 0

        # 3a. Aktualizacja 'odcinek_na_stronie' jeśli większy
        try:
            if latest_ready > s.odcinek_na_stronie:
                logger.info("%s: aktualizacja odcinek_na_stronie %d -> %d", s.nazwa, s.odcinek_na_stronie, latest_ready)
                update_cell(ws, s.row_idx, mapping["odcinek_na_stronie"] + 1, latest_ready)
                s.odcinek_na_stronie = latest_ready
        except APIError as e:
            problems.append(f"{s.nazwa}: błąd aktualizacji arkusza: {e}")

        # (opcjonalnie) aktualizuj liczba_odcinków jeżeli wykryto większy max
        try:
            if max_found > s.liczba_odcinków:
                logger.info("%s: aktualizacja liczba_odcinków %d -> %d", s.nazwa, s.liczba_odcinków, max_found)
                update_cell(ws, s.row_idx, mapping["liczba_odcinków"] + 1, max_found)
                s.liczba_odcinków = max_found
        except APIError as e:
            problems.append(f"{s.nazwa}: błąd aktualizacji liczby odcinków: {e}")

        # 3b. Jeżeli obejrzany < na_stronie – dodaj do listy powiadomień
        if s.obejrzany_odcinek < s.odcinek_na_stronie:
            new_items.append({
                "tytuł": s.nazwa,
                "nowy_odcinek": s.odcinek_na_stronie,
                "ostatni_obejrzany": s.obejrzany_odcinek,
                "link": s.link,
            })

    # 4. E-mail
    subject = "Nowe odcinki do obejrzenia – Sprawdzacz"
    body = build_email_body(new_items, problems)

    if always_send or new_items or problems:
        try:
            send_email(subject, body)
        except Exception as e:
            logger.exception("Błąd wysyłki e-mail: %s", e)
            return 3
    else:
        logger.info("Brak zmian – nie wysyłam e-maila.")

    logger.info("Zakończono.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
