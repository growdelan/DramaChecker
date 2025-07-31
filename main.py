#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os, re, sys, html, logging, smtplib
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
from email.message import EmailMessage

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from jinja2 import Template
import gspread
from gspread.exceptions import APIError, SpreadsheetNotFound, WorksheetNotFound

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO), format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

EPISODE_ANY_RE = re.compile(r'Odcinek\s*(\d+)', re.IGNORECASE)

DEFAULT_USER_AGENT = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/124.0 Safari/537.36'
)

COLUMN_ALIASES: Dict[str, List[str]] = {
    'nazwa': ['nazwa', 'tytuł', 'tytul'],
    'link': ['link', 'url'],
    'obejrzany_odcinek': ['obejrzany_odcinek', 'last_watched', 'obejrzany'],
    'odcinek_na_stronie': ['odcinek_na_stronie', 'last_on_site', 'na_stronie'],
    'liczba_odcinków': ['liczba_odcinków', 'liczba_odicnków', 'liczba_odc', 'max_odcinek'],
}

HTML_TEMPLATE = Template(r'''<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<title>Powiadomienia o nowych odcinkach z DramaQueen</title>
<style type="text/css">
  body{margin:0;padding:0;background:#f7f9fa;font-family:Arial,Helvetica,sans-serif;color:#333}
  a{color:#ff6699;text-decoration:none}
  .wrapper{width:100%;table-layout:fixed;background:#f7f9fa;padding:20px 0}
  .main{width:100%;max-width:600px;background:#fff;margin:0 auto;border-collapse:collapse;border:1px solid #e8ecef}
  .header{background:#ffeef3;padding:24px;text-align:center}
  .header h1{margin:0;font-size:24px;color:#cc3066}
  .episode-block{padding:24px 24px 16px 24px}
  .episode-title{font-size:18px;margin:0 0 8px 0;color:#222}
  .episode-update{font-size:14px;margin:0 0 12px 0;line-height:1.5em}
  .button{display:inline-block;padding:10px 22px;font-size:14px;background:#ff6699;color:#fff !important;border-radius:4px}
  .divider{height:1px;background:#f2f4f6;border:none;margin:0 24px}
  .footer{padding:16px 24px;font-size:12px;color:#999;text-align:center}
  @media only screen and (max-width:620px){.episode-block{padding:16px !important}.header h1{font-size:20px !important}}
</style>
</head>
<body>
<center class="wrapper">
<table class="main" role="presentation" cellpadding="0" cellspacing="0">
<tr><td class="header"><h1>Twoje nowe odcinki K-dram</h1></td></tr>

{% if new_items and new_items|length > 0 %}
  {% for d in new_items %}
    <tr><td class="episode-block">
      <h2 class="episode-title">{{ d.get('tytuł') or d.get('nazwa') }}</h2>
      <p class="episode-update">
        <strong>Update</strong>: obejrzano odcinek <strong>{{ d.get('ostatni_obejrzany') }}</strong>
        {% if d.get('liczba_odcinków') %} z <strong>{{ d.get('liczba_odcinków') }}</strong>{% endif %},
        nowy odcinek: <strong>{{ d.get('nowy_odcinek') }}</strong>.
      </p>
      {% if d.get('link') %}
        <a href="{{ d.get('link') }}" class="button" target="_blank">Zobacz nowy odcinek</a>
      {% endif %}
    </td></tr>
    {% if not loop.last %}<tr><td><hr class="divider"></td></tr>{% endif %}
  {% endfor %}
{% else %}
  <tr><td class="episode-block"><h2 class="episode-title">Brak nowych odcinków do obejrzenia.</h2></td></tr>
{% endif %}

<tr><td><hr class="divider"></td></tr>
<tr><td class="episode-block"><h2 class="episode-title">Problemy techniczne</h2>
  {% if problems and problems|length > 0 %}
    <ul style="padding-left:18px;margin:8px 0">
      {% for p in problems %}<li style="margin-bottom:6px">{{ p }}</li>{% endfor %}
    </ul>
  {% else %}<p class="episode-update">brak</p>{% endif %}
</td></tr>
<tr><td class="footer">Życzymy miłego seansu!</td></tr>
</table>
</center>
</body>
</html>''' )

@dataclass
class SeriesRow:
    row_idx: int
    nazwa: str
    link: str
    obejrzany_odcinek: int
    odcinek_na_stronie: int
    liczba_odcinków: int

    @property
    def is_done(self) -> bool:
        return self.obejrzany_odcinek == self.odcinek_na_stronie == self.liczba_odcinków


@dataclass
class EpisodeCheckResult:
    latest_ready: Optional[int]
    max_found: Optional[int]
    error: Optional[str] = None

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
        return int(re.sub(r'\D', '', s))
    except Exception:
        return default

def build_email_html(new_items: List[dict], problems: List[str]) -> str:
    new_items = new_items or []
    problems = problems or []
    try:
        return HTML_TEMPLATE.render(new_items=new_items, problems=problems)
    except Exception as e:
        logger.exception('Błąd renderowania HTML: %s', e)
        esc = html.escape(str(e))
        return f'<pre>Błąd generowania HTML: {esc}\nNowe: {len(new_items)}, Problemy: {len(problems)}</pre>'

def extract_episode_number(text: str) -> Optional[int]:
    m = EPISODE_ANY_RE.search(text)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            return None
    return None

def find_episodes(html_text: str) -> EpisodeCheckResult:
    try:
        soup = BeautifulSoup(html_text, 'html.parser')
        p_tags = soup.find_all('p', class_=lambda c: c and 'toggler' in c)
        latest_ready = None
        max_found = None
        for p in p_tags:
            num = extract_episode_number(p.get_text(' ', strip=True))
            if num is not None:
                if max_found is None or num > max_found:
                    max_found = num
            has_img = p.find('img') is not None
            if not has_img and num is not None:
                if latest_ready is None or num > latest_ready:
                    latest_ready = num
        if latest_ready is None and max_found is None:
            return EpisodeCheckResult(None, None, error='Nie znaleziono nagłówków odcinków.')
        return EpisodeCheckResult(latest_ready, max_found, None)
    except Exception as e:
        return EpisodeCheckResult(None, None, error=f'Błąd parsowania HTML: {e}')

def authenticate_gspread(service_account_file: str) -> gspread.Client:
    return gspread.service_account(filename=service_account_file)

def open_sheet(gc: gspread.Client, spreadsheet_title: str, worksheet_title: str):
    try:
        sh = gc.open(spreadsheet_title)
    except SpreadsheetNotFound as e:
        raise RuntimeError('Nie znaleziono arkusza.') from e
    try:
        ws = sh.worksheet(worksheet_title)
    except WorksheetNotFound:
        ws = sh.sheet1
        logger.warning('Nie znaleziono zakładki %s – używam pierwszej.', worksheet_title)
    return sh, ws

def map_headers(header_row: List[str]) -> Dict[str, int]:
    normalized = [str(h or '').strip().lower() for h in header_row]
    mapping: Dict[str, int] = {}
    for canon, aliases in COLUMN_ALIASES.items():
        for a in aliases:
            if a in normalized:
                mapping[canon] = normalized.index(a)
                break
    missing = [k for k in ('nazwa','link','obejrzany_odcinek','odcinek_na_stronie','liczba_odcinków') if k not in mapping]
    if missing:
        raise RuntimeError(f'Brak wymaganych kolumn: {missing}')
    return mapping

def read_series(ws) -> Tuple[List[SeriesRow], List[str], Dict[str, int]]:
    values = ws.get_all_values()
    if not values:
        raise RuntimeError('Arkusz jest pusty.')
    header = values[0]
    mapping = map_headers(header)
    rows: List[SeriesRow] = []
    for i, row in enumerate(values[1:], start=2):
        def get(idx: int) -> str:
            return row[idx] if idx < len(row) else ''
        rows.append(SeriesRow(
            row_idx=i,
            nazwa=get(mapping['nazwa']),
            link=get(mapping['link']),
            obejrzany_odcinek=parse_int(get(mapping['obejrzany_odcinek']), 0),
            odcinek_na_stronie=parse_int(get(mapping['odcinek_na_stronie']), 0),
            liczba_odcinków=parse_int(get(mapping['liczba_odcinków']), 0),
        ))
    return rows, header, mapping

def update_cell(ws, row_idx: int, col_idx: int, value: object):
    ws.update_cell(row_idx, col_idx, value)

def build_requests_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({'User-Agent': DEFAULT_USER_AGENT})
    php_sessid = os.environ.get('PHPSESSID')
    if php_sessid:
        s.cookies.set('PHPSESSID', php_sessid, domain='www.dramaqueen.pl')
    wp_logged_name = os.environ.get('WP_LOGGED_IN_COOKIE_NAME')
    wp_logged_val = os.environ.get('WP_LOGGED_IN_COOKIE_VALUE')
    if wp_logged_name and wp_logged_val:
        s.cookies.set(wp_logged_name, wp_logged_val, domain='www.dramaqueen.pl')
    wp_sec_name = os.environ.get('WP_SEC_COOKIE_NAME')
    wp_sec_val = os.environ.get('WP_SEC_COOKIE_VALUE')
    if wp_sec_name and wp_sec_val:
        s.cookies.set(wp_sec_name, wp_sec_val, domain='www.dramaqueen.pl')
    return s

def check_series(session: requests.Session, series: SeriesRow) -> EpisodeCheckResult:
    try:
        resp = session.get(series.link, timeout=60)
        if resp.status_code != 200:
            return EpisodeCheckResult(None, None, error=f'{series.nazwa}: HTTP {resp.status_code}')
        return find_episodes(resp.text)
    except Exception as e:
        return EpisodeCheckResult(None, None, error=f'{series.nazwa}: błąd pobierania: {e}')

def send_email(subject: str, html_body: str) -> None:
    smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')
    email_to  = os.environ.get('EMAIL_TO')
    email_from = os.environ.get('EMAIL_FROM', smtp_user)
    if not (smtp_user and smtp_pass and email_to):
        raise RuntimeError('Brak ustawień SMTP/EMAIL_TO')

    msg = EmailMessage()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = subject
    msg.add_alternative(html_body, subtype='html')

    with smtplib.SMTP(smtp_host, smtp_port, timeout=60) as server:
        server.ehlo()
        if smtp_port == 587:
            server.starttls(); server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        logger.info('Wysłano e-mail HTML do %s', email_to)

def main() -> int:
    load_dotenv()
    spreadsheet_title = os.environ.get('SHEET_TITLE', 'dramy')
    worksheet_title   = os.environ.get('WORKSHEET_TITLE', 'arkusz1')
    service_account_file = os.environ.get('GSPREAD_SERVICE_ACCOUNT_FILE', 'service_account.json')
    always_send = os.environ.get('ALWAYS_SEND', '1') in ('1','true','True','yes','tak')

    # 1. Sheets
    try:
        gc = authenticate_gspread(service_account_file)
        sh, ws = open_sheet(gc, spreadsheet_title, worksheet_title)
        rows, header, mapping = read_series(ws)
        logger.info('Wczytano %d wierszy', len(rows))
    except Exception as e:
        logger.exception('Błąd dostępu do Google Sheets: %s', e)
        try:
            send_email('Sprawdzacz odcinków – błąd Sheets', f'<pre>Błąd: {html.escape(str(e))}</pre>')
        except Exception:
            pass
        return 2

    session = build_requests_session()
    new_items: List[dict] = []
    problems: List[str] = []

    for s in rows:
        if s.is_done:
            continue
        if not s.link:
            problems.append(f'{s.nazwa}: brak linku w arkuszu')
            continue
        result = check_series(session, s)
        if result.error:
            problems.append(result.error)
            continue

        latest_ready = result.latest_ready or 0
        max_found = result.max_found or 0

        try:
            if latest_ready > s.odcinek_na_stronie:
                update_cell(ws, s.row_idx, mapping['odcinek_na_stronie'] + 1, latest_ready)
                s.odcinek_na_stronie = latest_ready
        except APIError as e:
            problems.append(f'{s.nazwa}: błąd aktualizacji arkusza: {e}')

        try:
            if max_found > s.liczba_odcinków:
                update_cell(ws, s.row_idx, mapping['liczba_odcinków'] + 1, max_found)
                s.liczba_odcinków = max_found
        except APIError as e:
            problems.append(f'{s.nazwa}: błąd aktualizacji liczby odcinków: {e}')

        if s.obejrzany_odcinek < s.odcinek_na_stronie:
            new_items.append({
                'tytuł': s.nazwa,
                'nowy_odcinek': s.odcinek_na_stronie,
                'ostatni_obejrzany': s.obejrzany_odcinek,
                'liczba_odcinków': s.liczba_odcinków,
                'link': s.link,
            })

    subject = 'Nowe odcinki do obejrzenia – Sprawdzacz'
    html_body = build_email_html(new_items, problems)

    if always_send or new_items or problems:
        try:
            send_email(subject, html_body)
        except Exception as e:
            logger.exception('Błąd wysyłki e-mail: %s', e)
            return 3
    else:
        logger.info('Brak zmian – e-mail nie został wysłany.')

    logger.info('Zakończono.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
