import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode('p', 'test123', props={"href": "https://www.google.com","target": "_blank",})
        self.assertEqual(node.props_to_html(), ' href="https://www.google.com" target="_blank"')
        
    def test_values(self):
        node = HTMLNode('div', 'Hello World', None, None)
        
        self.assertEqual(node.tag, 'div')
        
        self.assertEqual(node.value, 'Hello World')
        
        self.assertEqual(node.children, None)
        
        self.assertEqual(node.props, None)
        
    def test_repr(self):
        node = HTMLNode('div', 'Hello World', None, {"class": "primary"})
        self.assertEqual(repr(node), "HTMLNode: div, Hello World, children: None, {'class': 'primary'}")

class TestLeafNode(unittest.TestCase):
    def test_to_html_p(self):
        node = LeafNode("p", "Hello World",{"href":"https://google.com"})
        self.assertEqual(node.to_html(), '<p href="https://google.com">Hello World</p>')
    
    def test_to_html_div(self):
        node = LeafNode("div", "Hello World",{"href":"https://google.com"})
        self.assertEqual(node.to_html(), '<div href="https://google.com">Hello World</div>')
        
    def test_to_html_no_tag(self):
        node = LeafNode(None, "Hello World", {"href":"https://google.com"})
        self.assertEqual(node.to_html(), "Hello World")
        
class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )
        
    def test_to_html_with_multiple_children(self):
        child_node1 = LeafNode("b", "child1")
        child_node2 = LeafNode("p", "child2")
        child_node3 = LeafNode("div", "child3")
        parent_node = ParentNode("span", [child_node1, child_node2, child_node3])
        self.assertEqual(
            parent_node.to_html(),
            "<span><b>child1</b><p>child2</p><div>child3</div></span>"
        )
        
    def test_to_html_with_multiple_granchildren(self):
        grandchild_node1 = LeafNode("b", "grandchild1")
        grandchild_node2 = LeafNode("p", "grandchild2")
        grandchild_node3 = LeafNode("b", "grandchild3")
        child_node = ParentNode("span", [grandchild_node1, grandchild_node2, grandchild_node3])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild1</b><p>grandchild2</p><b>grandchild3</b></span></div>",
        )
        
        
if __name__ == "__main__":
    unittest.main()
    