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


class FlakyAuthenticator:
    def __init__(self, fail_attempts=1, message="Po logowaniu nie znaleziono wymaganych cookie sesyjnych."):
        self.calls = 0
        self.fail_attempts = fail_attempts
        self.message = message

    def ensure_session(self, session, force=False):
        self.calls += 1
        if self.calls <= self.fail_attempts:
            raise RuntimeError(self.message)
        session.cookies.set("wordpress_logged_in_test", "ok", domain="www.dramaqueen.pl")


class AuthSessionTests(unittest.TestCase):
    def test_extract_episode_number_accepts_exact_episode_and_final_label(self):
        self.assertEqual(6, main.extract_episode_number("Odcinek 6"))
        self.assertEqual(6, main.extract_episode_number("  Odcinek 6  "))
        self.assertEqual(10, main.extract_episode_number("Odcinek 10 - Finał"))
        self.assertEqual(10, main.extract_episode_number("Odcinek 10-Finał"))
        self.assertEqual(10, main.extract_episode_number("Odcinek 10 - finał"))
        self.assertEqual(10, main.extract_episode_number("Odcinek 10 - FINAŁ"))
        self.assertIsNone(
            main.extract_episode_number("Odcinek 6 Premiera w Korei: 31.03.2026")
        )
        self.assertIsNone(main.extract_episode_number("Odcinek 6 - wkrótce"))
        self.assertIsNone(main.extract_episode_number("Odcinek 10 - Final"))

    def test_find_episodes_ignores_labels_with_additional_description(self):
        html = """
        <p class="toggler">Odcinek 5</p>
        <p class="toggler">Odcinek 6 Premiera w Korei: 31.03.2026</p>
        <p class="toggler"><img src="locked.png">Odcinek 7</p>
        """

        result = main.find_episodes(html)

        self.assertIsNone(result.error)
        self.assertEqual(5, result.latest_ready)
        self.assertEqual(7, result.max_found)

    def test_find_episodes_returns_error_when_only_descriptive_labels_exist(self):
        html = """
        <p class="toggler">Odcinek 6 Premiera w Korei: 31.03.2026</p>
        <p class="toggler">Premiera w Korei: 31.03.2026</p>
        """

        result = main.find_episodes(html)

        self.assertEqual("Nie znaleziono nagłówków odcinków.", result.error)
        self.assertIsNone(result.latest_ready)
        self.assertIsNone(result.max_found)

    def test_find_episodes_accepts_unlocked_final_episode_label(self):
        html = """
        <p class="toggler">Odcinek 9</p>
        <p class="toggler">Odcinek 10 - Finał</p>
        """

        result = main.find_episodes(html)

        self.assertIsNone(result.error)
        self.assertEqual(10, result.latest_ready)
        self.assertEqual(10, result.max_found)

    def test_find_episodes_counts_locked_final_only_as_max_found(self):
        html = """
        <p class="toggler">Odcinek 9</p>
        <p class="toggler"><img src="locked.png">Odcinek 10 - Finał</p>
        """

        result = main.find_episodes(html)

        self.assertIsNone(result.error)
        self.assertEqual(9, result.latest_ready)
        self.assertEqual(10, result.max_found)

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

    def test_check_series_retries_auth_recovery_after_transient_failure(self):
        login_page = FakeResponse(
            url="https://www.dramaqueen.pl/wp-login.php?redirect_to=%2Fserial",
            text='<input id="user_login" name="log"><input id="user_pass" name="pwd"><input id="wp-submit">',
        )
        episode_page = FakeResponse(
            text="""
            <p class="toggler">Odcinek 9</p>
            <p class="toggler"><img src="locked.png">Odcinek 10</p>
            """,
        )
        session = FakeSession([login_page, episode_page])
        authenticator = FlakyAuthenticator(fail_attempts=1)
        series = main.SeriesRow(
            row_idx=2,
            nazwa="City Hunter",
            link="https://www.dramaqueen.pl/city-hunter",
            obejrzany_odcinek=7,
            odcinek_na_stronie=7,
            liczba_odcinków=20,
        )

        result = main.check_series(session, series, authenticator)

        self.assertIsNone(result.error)
        self.assertEqual(9, result.latest_ready)
        self.assertEqual(10, result.max_found)
        self.assertEqual(2, authenticator.calls)

    def test_check_series_returns_error_after_exhausted_auth_retries(self):
        login_page = FakeResponse(
            url="https://www.dramaqueen.pl/wp-login.php?redirect_to=%2Fserial",
            text='<input id="user_login" name="log"><input id="user_pass" name="pwd"><input id="wp-submit">',
        )
        session = FakeSession([login_page])
        authenticator = FlakyAuthenticator(fail_attempts=5)
        series = main.SeriesRow(
            row_idx=2,
            nazwa="City Hunter",
            link="https://www.dramaqueen.pl/city-hunter",
            obejrzany_odcinek=7,
            odcinek_na_stronie=7,
            liczba_odcinków=20,
        )

        result = main.check_series(session, series, authenticator)

        self.assertIsNotNone(result.error)
        self.assertIn("błąd pobierania", result.error or "")
        self.assertIn("Po logowaniu nie znaleziono wymaganych cookie sesyjnych", result.error or "")
        self.assertEqual(main.AUTH_RECOVERY_MAX_ATTEMPTS, authenticator.calls)

    def test_check_series_returns_auth_recovery_error_when_page_still_requires_auth(self):
        login_page = FakeResponse(
            url="https://www.dramaqueen.pl/wp-login.php?redirect_to=%2Fserial",
            text='<input id="user_login" name="log"><input id="user_pass" name="pwd"><input id="wp-submit">',
        )
        session = FakeSession([login_page, login_page, login_page])
        authenticator = FakeAuthenticator()
        series = main.SeriesRow(
            row_idx=2,
            nazwa="City Hunter",
            link="https://www.dramaqueen.pl/city-hunter",
            obejrzany_odcinek=7,
            odcinek_na_stronie=7,
            liczba_odcinków=20,
        )

        result = main.check_series(session, series, authenticator)

        self.assertIsNotNone(result.error)
        self.assertIn("nie udało się odzyskać zalogowanej sesji", result.error or "")
        self.assertEqual(main.AUTH_RECOVERY_MAX_ATTEMPTS, authenticator.calls)


if __name__ == "__main__":
    unittest.main()
