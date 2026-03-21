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

    def get(self, url, timeout=60):
        if not self._responses:
            raise AssertionError("Brak przygotowanej odpowiedzi dla FakeSession.")
        return self._responses.pop(0)


class FakeAuthenticator:
    def __init__(self):
        self.calls = 0

    def ensure_session(self, session, force=False):
        self.calls += 1
        session.cookies.set("wordpress_logged_in_test", "ok", domain="www.dramaqueen.pl")


class AuthSessionTests(unittest.TestCase):
    def test_extract_auth_cookies_filters_only_session_cookies(self):
        cookies = [
            {"name": "PHPSESSID", "value": "abc"},
            {"name": "wordpress_logged_in_test", "value": "def"},
            {"name": "analytics_cookie", "value": "ghi"},
        ]

        filtered = main.extract_auth_cookies(cookies)

        self.assertEqual(
            ["PHPSESSID", "wordpress_logged_in_test"],
            [cookie["name"] for cookie in filtered],
        )

    def test_extract_browser_session_cookies_keeps_auxiliary_browser_state(self):
        cookies = [
            {"name": "wordpress_logged_in_test", "value": "def"},
            {"name": "_lscache_vary", "value": "ghi"},
            {"name": "wordpress_test_cookie", "value": "ok"},
            {"name": "", "value": "ignored"},
        ]

        filtered = main.extract_browser_session_cookies(cookies)

        self.assertEqual(
            ["wordpress_logged_in_test", "_lscache_vary", "wordpress_test_cookie"],
            [cookie["name"] for cookie in filtered],
        )

    def test_response_requires_auth_detects_wordpress_login_form(self):
        response = FakeResponse(
            url="https://www.dramaqueen.pl/serial",
            text="""
            <html>
              <form>
                <input id="user_login" name="log">
                <input id="user_pass" name="pwd" type="password">
                <input id="wp-submit" type="submit">
              </form>
            </html>
            """,
        )

        self.assertTrue(main.response_requires_auth(response))

    def test_check_series_reauthenticates_and_retries_once(self):
        login_page = FakeResponse(
            url="https://www.dramaqueen.pl/wp-login.php?redirect_to=%2Fserial",
            text='<input id="user_login" name="log"><input id="user_pass" name="pwd"><input id="wp-submit">',
        )
        episode_page = FakeResponse(
            text="""
            <p class="toggler">Odcinek 7</p>
            <p class="toggler"><img src="locked.png">Odcinek 8</p>
            """,
        )
        session = FakeSession([login_page, episode_page])
        authenticator = FakeAuthenticator()
        series = main.SeriesRow(
            row_idx=2,
            nazwa="Test Drama",
            link="https://www.dramaqueen.pl/test-drama",
            obejrzany_odcinek=5,
            odcinek_na_stronie=5,
            liczba_odcinków=12,
        )

        result = main.check_series(session, series, authenticator)

        self.assertIsNone(result.error)
        self.assertEqual(7, result.latest_ready)
        self.assertEqual(8, result.max_found)
        self.assertEqual(1, authenticator.calls)

    def test_check_series_reports_missing_authenticator(self):
        login_page = FakeResponse(
            url="https://www.dramaqueen.pl/wp-login.php",
            text='<input id="user_login" name="log"><input id="user_pass" name="pwd"><input id="wp-submit">',
        )
        session = FakeSession([login_page])
        series = main.SeriesRow(
            row_idx=2,
            nazwa="Test Drama",
            link="https://www.dramaqueen.pl/test-drama",
            obejrzany_odcinek=1,
            odcinek_na_stronie=1,
            liczba_odcinków=12,
        )

        result = main.check_series(session, series)

        self.assertIn("brak skonfigurowanego automatycznego logowania", result.error or "")


if __name__ == "__main__":
    unittest.main()
