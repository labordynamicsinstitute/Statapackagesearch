"""Unit tests for tools/version.py."""
import unittest

from tools.version import Version, bump, next_version, parse, parse_tag, tag_of

# Tags as they exist in this repository: bare, pre-dating the vN.N.N rule.
LEGACY_TAGS = ["1.0.16", "1.0.20", "1.1.0"]


class TestParse(unittest.TestCase):
    def test_parses_plain_version(self):
        self.assertEqual(parse("1.1.1"), Version(1, 1, 1))

    def test_rejects_leading_v(self):
        self.assertIsNone(parse("v1.1.1"))

    def test_rejects_suffix(self):
        self.assertIsNone(parse("1.1.1-rc.1"))

    def test_rejects_two_parts(self):
        self.assertIsNone(parse("1.1"))

    def test_tolerates_surrounding_whitespace(self):
        self.assertEqual(parse(" 1.1.1\n"), Version(1, 1, 1))

    def test_parse_tag_requires_v(self):
        self.assertEqual(parse_tag("v1.2.3"), Version(1, 2, 3))
        self.assertIsNone(parse_tag("1.2.3"))

    def test_str_and_tag(self):
        self.assertEqual(str(Version(1, 2, 3)), "1.2.3")
        self.assertEqual(tag_of(Version(1, 2, 3)), "v1.2.3")


class TestBump(unittest.TestCase):
    def test_patch(self):
        self.assertEqual(bump(Version(1, 1, 1), "patch"), Version(1, 1, 2))

    def test_minor_resets_patch(self):
        self.assertEqual(bump(Version(1, 1, 7), "minor"), Version(1, 2, 0))

    def test_major_resets_minor_and_patch(self):
        self.assertEqual(bump(Version(1, 1, 7), "major"), Version(2, 0, 0))

    def test_rejects_unknown_part(self):
        with self.assertRaises(ValueError):
            bump(Version(1, 1, 1), "epoch")


class TestNextVersion(unittest.TestCase):
    def test_patch_is_the_default(self):
        self.assertEqual(next_version("1.1.1", tags=[]), Version(1, 1, 2))

    def test_minor(self):
        self.assertEqual(next_version("1.1.1", "minor", tags=[]),
                         Version(1, 2, 0))

    def test_legacy_bare_tags_do_not_block(self):
        self.assertEqual(next_version("1.0.30", tags=LEGACY_TAGS + ["1.0.31"]),
                         Version(1, 0, 31))

    def test_override_wins(self):
        self.assertEqual(next_version("1.1.1", override="1.1.1", tags=[]),
                         Version(1, 1, 1))

    def test_override_rejects_garbage(self):
        with self.assertRaises(ValueError):
            next_version("1.1.1", override="v1.2.0", tags=[])

    def test_refuses_existing_tag(self):
        with self.assertRaises(ValueError):
            next_version("1.1.1", tags=["v1.1.2"])
        with self.assertRaises(ValueError):
            next_version("1.1.1", override="1.1.1", tags=["v1.1.1"])

    def test_override_may_not_go_backwards(self):
        with self.assertRaises(ValueError):
            next_version("1.1.1", override="1.1.0", tags=[])

    def test_unparseable_current_without_override_is_an_error(self):
        with self.assertRaises(ValueError):
            next_version("1.0.30-draft", tags=[])


if __name__ == "__main__":
    unittest.main()
