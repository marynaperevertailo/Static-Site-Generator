import unittest

from inline_markdown import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
)
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_code_in_middle(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_bold(self):
        node = TextNode("This is **bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_italic(self):
        node = TextNode("An _italic_ word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(
            new_nodes,
            [
                TextNode("An ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_multiple_bold_in_one_string(self):
        node = TextNode("**first** and **second**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("first", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("second", TextType.BOLD),
            ],
        )

    def test_no_delimiter_returns_same_node(self):
        node = TextNode("Plain text without any markup", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [TextNode("Plain text without any markup", TextType.TEXT)],
        )

    def test_non_text_node_passes_through(self):
        node = TextNode("already bold", TextType.BOLD)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [TextNode("already bold", TextType.BOLD)])

    def test_unmatched_delimiter_raises(self):
        node = TextNode("This is `broken markdown", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_multiple_input_nodes(self):
        nodes = [
            TextNode("First `code1` here", TextType.TEXT),
            TextNode("untouched bold", TextType.BOLD),
            TextNode("Second `code2` there", TextType.TEXT),
        ]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("First ", TextType.TEXT),
                TextNode("code1", TextType.CODE),
                TextNode(" here", TextType.TEXT),
                TextNode("untouched bold", TextType.BOLD),
                TextNode("Second ", TextType.TEXT),
                TextNode("code2", TextType.CODE),
                TextNode(" there", TextType.TEXT),
            ],
        )


class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_multiple_images(self):
        text = "Here is ![one](https://a.com/1.png) and ![two](https://a.com/2.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [
                ("one", "https://a.com/1.png"),
                ("two", "https://a.com/2.png"),
            ],
            matches,
        )

    def test_extract_no_images(self):
        matches = extract_markdown_images("Plain text with no images at all")
        self.assertListEqual([], matches)

    def test_extract_images_ignores_links(self):
        text = "A [link](https://boot.dev) and an ![img](https://i.com/a.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("img", "https://i.com/a.png")], matches)


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("to boot dev", "https://www.boot.dev")], matches)

    def test_extract_multiple_links(self):
        text = "[one](https://a.com) and [two](https://b.com)"
        matches = extract_markdown_links(text)
        self.assertListEqual(
            [("one", "https://a.com"), ("two", "https://b.com")],
            matches,
        )

    def test_extract_links_ignores_images(self):
        text = "An ![img](https://i.com/a.png) and a [link](https://boot.dev)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("link", "https://boot.dev")], matches)

    def test_extract_no_links(self):
        matches = extract_markdown_links("Just plain prose here")
        self.assertListEqual([], matches)


class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image",
                    TextType.IMAGE,
                    "https://i.imgur.com/3elNhQu.png",
                ),
            ],
            new_nodes,
        )

    def test_split_image_at_start(self):
        node = TextNode(
            "![start](https://a.com/x.png) and then text",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("start", TextType.IMAGE, "https://a.com/x.png"),
                TextNode(" and then text", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_image_at_end(self):
        node = TextNode(
            "Text and then ![end](https://a.com/y.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("Text and then ", TextType.TEXT),
                TextNode("end", TextType.IMAGE, "https://a.com/y.png"),
            ],
            new_nodes,
        )

    def test_split_no_images(self):
        node = TextNode("Plain text with no images", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_split_non_text_node_passes_through(self):
        node = TextNode("already bold", TextType.BOLD)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)


class TestSplitNodesLink(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube",
                    TextType.LINK,
                    "https://www.youtube.com/@bootdotdev",
                ),
            ],
            new_nodes,
        )

    def test_split_link_at_start(self):
        node = TextNode("[boot](https://boot.dev) is great", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("boot", TextType.LINK, "https://boot.dev"),
                TextNode(" is great", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_no_links(self):
        node = TextNode("Plain text with no links", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_split_links_does_not_match_images(self):
        node = TextNode(
            "An image ![pic](https://a.com/x.png) and a [link](https://boot.dev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("An image ![pic](https://a.com/x.png) and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            new_nodes,
        )


class TestTextToTextNodes(unittest.TestCase):
    def test_all_types(self):
        # Приклад прямо з завдання — усі типи в одному рядку
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image",
                    TextType.IMAGE,
                    "https://i.imgur.com/fJRm4Vk.jpeg",
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )

    def test_plain_text_only(self):
        # Без жодного форматування — один TEXT вузол на виході
        nodes = text_to_textnodes("Just some plain text")
        self.assertListEqual([TextNode("Just some plain text", TextType.TEXT)], nodes)

    def test_only_bold(self):
        nodes = text_to_textnodes("**only bold**")
        self.assertListEqual([TextNode("only bold", TextType.BOLD)], nodes)


if __name__ == "__main__":
    unittest.main()
