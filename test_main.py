import os
import tempfile
import unittest
from unittest import mock

os.environ.setdefault("GOOGLE_API_KEY", "x" * 24)

import main


class FakePage:
    def get_text(self):
        return "resume text"


class BrokenPage:
    def get_text(self):
        raise RuntimeError("broken pdf")


class FakeDoc(list):
    def __init__(self, *pages):
        super().__init__(pages or [FakePage()])
        self.closed = False

    def close(self):
        self.closed = True


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

    def test_returns_empty_string_for_runtime_pdf_read_error(self):
        fake_doc = FakeDoc(BrokenPage())

        with mock.patch.object(main.os.path, "isfile", return_value=True):
            with mock.patch.object(main.os.path, "isdir", return_value=False):
                with mock.patch.object(main.fitz, "open", return_value=fake_doc):
                    self.assertEqual(main.getPdfText("resume.pdf"), "")

        self.assertTrue(fake_doc.closed)


if __name__ == "__main__":
    unittest.main()
