import os
import tempfile
import unittest
from unittest import mock

os.environ.setdefault("GOOGLE_API_KEY", "x" * 24)

import main


class FakePage:
    def get_text(self):
        return "resume text"


class FakeDoc(list):
    def __init__(self):
        super().__init__([FakePage()])

    def close(self):
        pass


class GetPdfTextTests(unittest.TestCase):
    def test_expands_environment_variables_in_resume_path(self):
        env_name = "AI_RESUME_SCANNER_TEST_DIR"
        env_value = tempfile.gettempdir()
        os.environ[env_name] = env_value

        input_path = f'%{env_name}%\\resume.pdf'
        expected_path = os.path.normpath(os.path.join(env_value, "resume.pdf"))

        with mock.patch.object(main.os.path, "isfile", side_effect=lambda path: path == expected_path):
            with mock.patch.object(main.os.path, "isdir", return_value=False):
                with mock.patch.object(main.fitz, "open", return_value=FakeDoc()) as mock_open:
                    self.assertEqual(main.getPdfText(input_path), "resume text")

        mock_open.assert_called_once_with(expected_path)


if __name__ == "__main__":
    unittest.main()
