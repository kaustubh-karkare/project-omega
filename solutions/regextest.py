import regex
import unittest


class RegexTest(unittest.TestCase):

    def test_basic_elements(self):
        self.assertEqual(regex.check(r'abcde', 'abcde'), True)
        self.assertEqual(regex.check(r'abcde', 'abcdf'), False)

        self.assertEqual(regex.check(r'a\d?\w+\s*e', 'abcde'), True)
        self.assertEqual(regex.check("^a[b-k]{2}$", "abcde"), False)

        self.assertEqual(regex.check(r'.*', 'ab12 _'), True)
        self.assertEqual(regex.check(r'.*', ''), True)
        self.assertEqual(regex.check(r'.+', 'ab12 _'), True)
        self.assertEqual(regex.check(r'.+', ''), False)
        self.assertEqual(regex.check(r'\d+', 'abcde'), False)

        self.assertEqual(regex.check(r'abc\sde', 'abc de'), True)
        self.assertEqual(regex.check(r'abs\Sde', 'abc de'), False)

        self.assertEqual(regex.check(r'a{2}bcd', 'aabcd'), True)
        self.assertEqual(regex.check(r'a{2,3}bcd', 'abcd'), False)
        self.assertEqual(regex.check(r'a{2,3}bcd', 'aabcd'), True)
        self.assertEqual(regex.check(r'a{2,3}bcd', 'aaabcd'), True)
        self.assertEqual(regex.check(r'^a{2,3}bcd', 'aaaabcd'), False)
        self.assertEqual(regex.check(r'a{2,3}bcd', 'aaaabcd'), True)

    def test_character_class(self):
        self.assertEqual(regex.check(r'a[b]cdef', 'abcdef'), True)
        self.assertEqual(regex.check(r'a[B]cdef', 'abcdef'), False)

        self.assertEqual(regex.check(r'a[\w]cdef', 'abcdef'), True)
        self.assertEqual(regex.check(r'a[^\w]cdef', 'abcdef'), False)
        self.assertEqual(regex.check(r'a[\W]cdef', 'abcdef'), False)

        self.assertEqual(regex.check(r'a[\d]cdef', 'a9cdef'), True)
        self.assertEqual(regex.check(r'a[\d]cdef', 'a cdef'), False)

        self.assertEqual(regex.check(r'a[\d]?cdef', 'acdef'), True)
        self.assertEqual(regex.check(r'a[\w]?cdef', 'abcdef'), True)
        self.assertEqual(regex.check(r'[\w]+', 'abc123_'), True)
        self.assertEqual(regex.check(r'[\w]+', ''), False)
        self.assertEqual(regex.check(r'[\w]*', ''), True)

        self.assertEqual(regex.check(r'a[b]*cd[e]*f', 'acdf'), True)
        self.assertEqual(regex.check(r'a[b]*cd[e]*f', 'abcdeeeef'), True)
        self.assertEqual(regex.check(r'a[a-z0-9]+', 'aAbcd12'), False)
        self.assertEqual(regex.check(r'abcde', 'bbabcde'), True)

        self.assertEqual(regex.check(r'[abc]{2,3}', 'a'), False)
        self.assertEqual(regex.check(r'[abc]{2,3}', 'bc'), True)


if __name__ == '__main__':
    unittest.main()
