import unittest
from pathlib import Path

import app


class FormattingTests(unittest.TestCase):
    def test_srt_timestamp(self):
        self.assertEqual(app._fmt_time(3661.125), "01:01:01,125")

    def test_vtt_timestamp(self):
        self.assertEqual(app._fmt_time(61.5, vtt=True), "00:01:01.500")

    def test_human_duration(self):
        self.assertEqual(app._fmt_hms(3661), "1h 01m 01s")


class TranscriptFileTests(unittest.TestCase):
    def test_empty_transcript_does_not_create_file(self):
        self.assertIsNone(app.save_transcript("  ", "plain"))

    def test_subtitle_uses_expected_extension(self):
        path = app.save_transcript("subtitle", "srt")
        self.assertIsNotNone(path)
        try:
            transcript = Path(path)
            self.assertEqual(transcript.suffix, ".srt")
            self.assertEqual(transcript.read_text(encoding="utf-8"), "subtitle")
        finally:
            Path(path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
