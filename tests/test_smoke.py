import unittest

import requests

import main


class FakeResponse:
    def __init__(self, status_code=200, url="https://www.dramaqueen.pl/serial", text=""):
        self.status_code = status_code
        self.url = url
        self.text = text


class FakeSession:
    def __init__(self, responses):
        self._responses = list(responses)
        self.cookies = requests.Session().cookies
        self.headers = {}

    def get(self, url, timeout=60):
        if not self._responses:
            raise AssertionError(f"Brak przygotowanej odpowiedzi dla URL {url}.")
        return self._responses.pop(0)


class FakeAuthenticator:
    def __init__(self):
        self.calls = 0

    def ensure_session(self, session, force=False):
        self.calls += 1
        session.cookies.set(
            "wordpress_logged_in_test",
            "ok",
            domain="www.dramaqueen.pl",
            path="/",
        )
        session.cookies.set(
            "wordpress_test_cookie",
            "WP Cookie check",
            domain="www.dramaqueen.pl",
            path="/",
        )


class FakeWorksheet:
    def __init__(self):
        self.values = [
            [
                "nazwa",
                "link",
                "obejrzany_odcinek",
                "odcinek_na_stronie",
                "liczba_odcinków",
            ],
            [
                "Smoke Drama",
                "https://www.dramaqueen.pl/drama/koreanska/smoke-drama/",
                "1",
                "1",
                "12",
            ],
        ]
        self.updated_cells = []

    def get_all_values(self):
        return self.values

    def update_cell(self, row_idx, col_idx, value):
        self.updated_cells.append((row_idx, col_idx, value))


class SmokeFlowTests(unittest.TestCase):
    def test_process_user_handles_reauth_updates_sheet_and_sends_email(self):
        login_page = FakeResponse(
            url="https://www.dramaqueen.pl/wp-login.php?redirect_to=%2Fserial",
            text='<input id="user_login" name="log"><input id="user_pass" name="pwd"><input id="wp-submit">',
        )
        episode_page = FakeResponse(
            url="https://www.dramaqueen.pl/drama/koreanska/smoke-drama/",
            text="""
            <p class="toggler">Odcinek 4</p>
            <p class="toggler"><img src="locked.png">Odcinek 5</p>
            """,
        )
        session = FakeSession([login_page, episode_page])
        authenticator = FakeAuthenticator()
        worksheet = FakeWorksheet()
        sent_messages = []

        original_authenticate_gspread = main.authenticate_gspread
        original_open_sheet = main.open_sheet
        original_send_email = main.send_email
        try:
            main.authenticate_gspread = lambda service_account_file: object()
            main.open_sheet = lambda gc, spreadsheet_title, worksheet_title: (
                object(),
                worksheet,
            )

            def fake_send_email(subject, html_body, email_to):
                sent_messages.append(
                    {
                        "subject": subject,
                        "html_body": html_body,
                        "email_to": email_to,
                    }
                )

            main.send_email = fake_send_email

            cfg = main.UserConfig(
                sheet_title="dramy",
                worksheet_title="Arkusz1",
                email_to="example@example.com",
                always_send=True,
                service_account_file="service_account.json",
            )

            result = main.process_user(cfg, session, authenticator)

            self.assertEqual(0, result)
            self.assertEqual(1, authenticator.calls)
            self.assertEqual([(2, 4, 4)], worksheet.updated_cells)
            self.assertEqual(1, len(sent_messages))
            self.assertIn("Smoke Drama", sent_messages[0]["html_body"])
            self.assertIn("nowy odcinek", sent_messages[0]["html_body"])
            self.assertEqual("example@example.com", sent_messages[0]["email_to"])
        finally:
            main.authenticate_gspread = original_authenticate_gspread
            main.open_sheet = original_open_sheet
            main.send_email = original_send_email

    def test_process_user_ignores_descriptive_label_and_does_not_false_positive(self):
        login_page = FakeResponse(
            url="https://www.dramaqueen.pl/wp-login.php?redirect_to=%2Fserial",
            text='<input id="user_login" name="log"><input id="user_pass" name="pwd"><input id="wp-submit">',
        )
        episode_page = FakeResponse(
            url="https://www.dramaqueen.pl/drama/koreanska/climax/",
            text="""
            <p class="toggler">Odcinek 5</p>
            <p class="toggler">Odcinek 6 Premiera w Korei: 31.03.2026</p>
            """,
        )
        session = FakeSession([login_page, episode_page])
        authenticator = FakeAuthenticator()
        worksheet = FakeWorksheet()
        worksheet.values[1][0] = "Climax"
        worksheet.values[1][1] = "https://www.dramaqueen.pl/drama/koreanska/climax/"
        worksheet.values[1][2] = "5"
        worksheet.values[1][3] = "5"
        sent_messages = []

        original_authenticate_gspread = main.authenticate_gspread
        original_open_sheet = main.open_sheet
        original_send_email = main.send_email
        try:
            main.authenticate_gspread = lambda service_account_file: object()
            main.open_sheet = lambda gc, spreadsheet_title, worksheet_title: (
                object(),
                worksheet,
            )

            def fake_send_email(subject, html_body, email_to):
                sent_messages.append(
                    {
                        "subject": subject,
                        "html_body": html_body,
                        "email_to": email_to,
                    }
                )

            main.send_email = fake_send_email

            cfg = main.UserConfig(
                sheet_title="dramy",
                worksheet_title="Arkusz1",
                email_to="example@example.com",
                always_send=False,
                service_account_file="service_account.json",
            )

            result = main.process_user(cfg, session, authenticator)

            self.assertEqual(0, result)
            self.assertEqual(1, authenticator.calls)
            self.assertEqual([], worksheet.updated_cells)
            self.assertEqual([], sent_messages)
        finally:
            main.authenticate_gspread = original_authenticate_gspread
            main.open_sheet = original_open_sheet
            main.send_email = original_send_email


if __name__ == "__main__":
    unittest.main()
