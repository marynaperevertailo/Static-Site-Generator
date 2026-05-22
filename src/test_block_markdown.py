import unittest

from block_markdown import (
    BlockType,
    block_to_block_type,
    markdown_to_blocks,
    markdown_to_html_node,
)


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_excessive_newlines(self):
        md = "First block\n\n\n\n\nSecond block"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["First block", "Second block"])

    def test_single_block(self):
        md = "Just one paragraph here with no breaks"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Just one paragraph here with no breaks"])

    def test_leading_and_trailing_whitespace(self):
        md = "\n\n   First block   \n\n   Second block   \n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["First block", "Second block"])

    def test_empty_string(self):
        self.assertEqual(markdown_to_blocks(""), [])


class TestBlockToBlockType(unittest.TestCase):
    def test_paragraph(self):
        block = "This is just a normal paragraph with some words."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_heading_h1(self):
        self.assertEqual(block_to_block_type("# Heading one"), BlockType.HEADING)

    def test_heading_h6(self):
        self.assertEqual(block_to_block_type("###### Smallest heading"), BlockType.HEADING)

    def test_heading_seven_hashes_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("####### Too many hashes"),
            BlockType.PARAGRAPH,
        )

    def test_heading_no_space_is_paragraph(self):
        self.assertEqual(block_to_block_type("#NoSpace"), BlockType.PARAGRAPH)

    def test_code_block(self):
        block = "```\nprint(\'hello\')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_quote_single_line(self):
        self.assertEqual(block_to_block_type("> Wise words"), BlockType.QUOTE)

    def test_quote_multiline(self):
        block = "> first line\n> second line\n> third line"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_one_line_missing_marker(self):
        block = "> first line\nsecond line without marker"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_unordered_list(self):
        block = "- item one\n- item two\n- item three"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_no_space_is_paragraph(self):
        block = "-item one\n-item two"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list(self):
        block = "1. first\n2. second\n3. third"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_wrong_start_is_paragraph(self):
        block = "2. first\n3. second"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_skipped_number_is_paragraph(self):
        block = "1. first\n3. third"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)


class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_heading(self):
        md = "# This is a heading"
        node = markdown_to_html_node(md)
        self.assertEqual(node.to_html(), "<div><h1>This is a heading</h1></div>")

    def test_multiple_heading_levels(self):
        md = """
# H1 here

## H2 there

###### Smallest heading
"""
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><h1>H1 here</h1><h2>H2 there</h2><h6>Smallest heading</h6></div>",
        )

    def test_quote(self):
        md = "> first line of quote\n> second line of quote"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><blockquote>first line of quote second line of quote</blockquote></div>",
        )

    def test_unordered_list(self):
        md = "- first item\n- second **bold** item\n- third item"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><ul><li>first item</li><li>second <b>bold</b> item</li><li>third item</li></ul></div>",
        )

    def test_ordered_list(self):
        md = "1. one\n2. two\n3. three"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><ol><li>one</li><li>two</li><li>three</li></ol></div>",
        )


if __name__ == "__main__":
    unittest.main()
