"""Regression checks for HTML formatting without external dependencies."""
import unittest

from build import format_html


class FormatHTMLTests(unittest.TestCase):
    def test_indents_structure_with_two_spaces(self):
        source = '<!doctype html><html lang="en"><body><section><h2>Title</h2><p>Text.</p></section></body></html>'
        self.assertEqual(format_html(source), "\n".join([
            '<!doctype html>',
            '<html lang="en">',
            '  <body>',
            '    <section>',
            '      <h2>Title</h2>',
            '      <p>Text.</p>',
            '    </section>',
            '  </body>',
            '</html>',
            '',
        ]))

    def test_preserves_inline_punctuation_and_adjacent_links(self):
        authors = '<p><strong>Alice*</strong>, <a href="https://example.com/">Bob</a> &amp; Carol.</p>'
        links = '<a href="https://example.com/a">A</a><a href="https://example.com/b">B</a>'
        result = format_html('<div>' + authors + '<div>' + links + '</div></div>')
        self.assertIn(authors, result)
        self.assertIn(links, result)

    def test_preserves_intentional_text_whitespace(self):
        fragments = [
            '<p class="additional-interests">AI and Web3.\nEntrepreneurship.</p>',
            '<pre>  leading spaces\n    indentation\n</pre>',
            '<textarea>  input\nsecond line </textarea>',
            '<script>if (a < b && b > 0) {\n  run("<div>");\n}</script>',
            '<style>p::after { content: "a > b"; }\n</style>',
        ]
        for fragment in fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, format_html('<div>' + fragment + '</div>'))

    def test_preserves_svg_attributes_entities_and_comments(self):
        svg = '<svg viewBox="0 0 24 24"><symbol id="icon-X"><path d="M0 0h2"/></symbol></svg>'
        result = format_html('<body><!-- Keep this comment. -->' + svg + '<p>A&nbsp;B &#169; &amp; C</p></body>')
        self.assertIn('<svg viewBox="0 0 24 24">', result)
        self.assertIn('<symbol id="icon-X">', result)
        self.assertIn('<path d="M0 0h2"/>', result)
        self.assertIn('<!-- Keep this comment. -->', result)
        self.assertIn('<p>A&nbsp;B &#169; &amp; C</p>', result)

    def test_is_repeatable_with_raw_text_and_inline_groups(self):
        source = '<html><body><div><p>First.\nSecond.</p><div><a href="#a">A</a> <a href="#b">B</a></div><button><img src="one.jpg"><img src="two.jpg"></button></div></body></html>'
        formatted = format_html(source)
        self.assertEqual(format_html(formatted), formatted)
        self.assertTrue(formatted.endswith('\n'))

    def test_preserves_unicode_line_separators(self):
        source = '<div><p>One\u2028two</p><p>Three</p></div>'
        result = format_html(source)
        self.assertIn('<p>One\u2028two</p>', result)
        self.assertIn('<p>Three</p>', result)

    def test_rejects_incomplete_or_mismatched_markup(self):
        for source in ('<div><p>Missing end', '<div></section>'):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    format_html(source)


if __name__ == '__main__':
    unittest.main()
