from analyzer import Expression


class SentenceTreeNode:
    def __init__(self, leaf: bool=False) -> None:
        self.leaf = leaf
        self.word = ""
        self.props = []
        self.depth = 0
        self.child = []


class SentenceTree:
    def __init__(self) -> None:
        self.root = SentenceTreeNode(True)
    
    def print_tree(
        self,
        cur_node: SentenceTreeNode,
        last=True,
        header=''
    ) -> None:
        elbow = "└──"
        pipe = "│  "
        tee = "├──"
        blank = "   "

        print(header + (elbow if last else tee) + cur_node.word)

        if not cur_node.child:
            return

        for i, c in enumerate(cur_node.child):
            self.print_tree(
                cur_node=c,
                last=i == len(cur_node.child) - 1,
                header=header + (blank if last else pipe)
            )

    def insert_from_words(
        self,
        cur_node: SentenceTreeNode,
        words: list,
        cur_word: Expression=None,
        last: bool=True,
        cur_depth: int=0
    ) -> None:
        if cur_node.child == []:
            cur_node.word = cur_word.raw_words
            cur_node.props = cur_word.properties
            cur_node.depth = cur_depth

        if not words:
            cur_depth = 0
            return
        
        for i, c in enumerate(words):
            new_node = SentenceTreeNode()
            cur_node.child.append(new_node)

            self.insert_from_words(
                cur_node=new_node,
                words=c.children,
                cur_word=c,
                last=i == len(words) - 1,
                cur_depth=cur_depth + 1
            )
