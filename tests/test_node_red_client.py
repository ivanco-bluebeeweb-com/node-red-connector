import unittest

import node_red_client as api


class Response:
    def __init__(self, status_code, body=None):
        self.status_code = status_code
        self.body = body if body is not None else {}


class NodeRedClientTests(unittest.TestCase):
    def test_normalize_base_url_requires_https(self):
        self.assertEqual(
            api.normalize_base_url(" https://flows.example.com/ "),
            "https://flows.example.com",
        )
        with self.assertRaises(api.ClientFail) as error:
            api.normalize_base_url("http://flows.example.com")
        self.assertEqual(error.exception.code, "NODE_RED_INVALID_URL")

    def test_api_error_mapping_is_actionable(self):
        for status, code in (
            (401, "NODE_RED_TOKEN_REJECTED"),
            (403, "NODE_RED_FORBIDDEN"),
            (404, "NODE_RED_UNSUPPORTED"),
            (429, "NODE_RED_RATE_LIMITED"),
            (500, "NODE_RED_PROVIDER_ERROR"),
        ):
            with self.subTest(status=status), self.assertRaises(api.ClientFail) as error:
                api.check(Response(status), "/flows")
            self.assertEqual(error.exception.code, code)

    def test_json_body_and_empty_success_are_normalized(self):
        self.assertEqual(api.check(Response(200, '{"flows": []}'), "/flows"), {"flows": []})
        self.assertEqual(api.check(Response(204), "/flows"), {})


if __name__ == "__main__":
    unittest.main()
