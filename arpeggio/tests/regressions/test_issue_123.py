from arpeggio.cleanpeg import ParserPEG

grammar = r'''
Root = 'a'
BlockComment = r'/\*.*?\*/'
LineComment = r'//[^\r\n]*'
Comment = LineComment / BlockComment
'''

def test_issue_123():

    parser = ParserPEG(grammar, 'Root', 'Comment')
    parser.parse(r'''
    // This is comment
    a
    //
    ''')
