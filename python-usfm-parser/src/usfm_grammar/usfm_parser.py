'''The core logics of converting the syntax tree to other formats'''

from enum import Enum
from importlib import resources
import re

from tree_sitter import Language, Parser
from lxml import etree

class Filter(str, Enum):
    '''Defines the values of filter option'''
    ALL = "all"
    SCRIPTURE_BCV = "scripture-bcv"
    SCRIPTURE_PARAGRAPHS = "scripture-paragraph"
    NOTES = "notes"
    NOTES_TEXT = "note-text"

class Filter_new(str, Enum):
    '''Defines the values of filter options'''
    BOOK_HEADERS = "book-header-introduction-markers"
    PARAS_N_TITLES = 'paragraphs-quotes-lists-tables-sectionheadings'
    SCRIPTURE_TEXT = 'verse-texts'
    NOTES = "footnotes-and-crossrefs"
    WORD_EMBEDDINGS = "character-level-markers"
    MILESTONES = "milestones-namespaces"
    STUDY_BIBLE = "sidebars-extended-contents"

class Format(str, Enum):
    '''Defines the valid values for output formats'''
    JSON = "json"
    CSV = "table"
    ST = "syntax-tree"
    USX = "usx"
    MD = "markdown"

lang_file = resources.path('usfm_grammar','my-languages.so')
USFM_LANGUAGE = Language(str(lang_file), 'usfm3')
parser = Parser()
parser.set_language(USFM_LANGUAGE)

PARA_STYLE_MARKERS = ["h", "toc", "toca" #identification
                    "imt", "is", "ip", "ipi", "im", "imi", "ipq", "imq", "ipr", "iq", "ib",
                    "ili", "iot", "io", "iex", "imte", "ie", # intro
                    "mt", "mte", "cl", "cd", "ms", "mr", "s", "sr", "r", "d", "sp", "sd", #titles
                    "q", "qr", "qc", "qa", "qm", "qd", #poetry
                    "lh", "li", "lf", "lim", "litl" #lists
                    ]

NOTE_MARKERS = ["f", "fe", "ef", "efe", "x", "ex"]
CHAR_STYLE_MARKERS = [ "add", "bk", "dc", "ior", "iqt", "k", "litl", "nd", "ord", "pn",
                    "png", "qac", "qs", "qt", "rq", "sig", "sls", "tl", "wj", # Special-text
                    "em", "bd", "bdit", "it", "no", "sc", "sup", # character styling
                     "rb", "pro", "w", "wh", "wa", "wg", #special-features
                     "lik", "liv", #structred list entries
                     "jmp",
                     "fr", "ft", "fk", "fq", "fqa", "fl", "fw", "fp", "fv", "fdc", #footnote-content
                     "xo", "xop", "xt", "xta", "xk", "xq", "xot", "xnt", "xdc" #crossref-content
                     ]
NESTED_CHAR_STYLE_MARKERS = [item+"Nested" for item in CHAR_STYLE_MARKERS]
DEFAULT_ATTRIB_MAP = {"w":"lemma", "rb":"gloss", "xt":"link-href", "fig":"alt"}
TABLE_CELL_MARKERS = ["tc", "th", "tcr", "thr"]

ANY_VALID_MARKER = PARA_STYLE_MARKERS+NOTE_MARKERS+CHAR_STYLE_MARKERS+\
                    NESTED_CHAR_STYLE_MARKERS+TABLE_CELL_MARKERS

def node_2_usx(node, usfm_bytes, parent_xml_node, xml_root_node):
    '''check each node and based on the type convert to corresponding xml element'''
    # print("working with node: ", node, "\n")
    if node.type == "id":
        id_captures = USFM_LANGUAGE.query('''(id (bookcode) @book-code
                                                    (description) @desc)''').captures(node)
        code = None
        desc = None
        for tupl in id_captures:
            if tupl[1] == "book-code":
                code = usfm_bytes[tupl[0].start_byte:tupl[0].end_byte].decode('utf-8')
            elif tupl[1] == 'desc':
                desc = usfm_bytes[tupl[0].start_byte:tupl[0].end_byte].decode('utf-8')
        book_xml_node = etree.SubElement(parent_xml_node, "book")
        book_xml_node.set("code", code)
        book_xml_node.set("style", "id")
        if desc is not None and desc.strip() != "":
            book_xml_node.text = desc.strip()
    elif node.type == "chapter":
        chap_cap = USFM_LANGUAGE.query('''(c (chapterNumber) @chap-num)''').captures(node)[0]
        chap_num = usfm_bytes[chap_cap[0].start_byte:chap_cap[0].end_byte].decode('utf-8')
        ref = parent_xml_node.find("book").attrib['code']+" "+chap_num
        chap_xml_node = etree.SubElement(parent_xml_node, "chapter")
        chap_xml_node.set("number", chap_num)
        chap_xml_node.set("style", "c")
        chap_xml_node.set("sid", ref)
        for child in node.children[1:]:
            node_2_usx(child, usfm_bytes, parent_xml_node, xml_root_node)

        prev_verses = xml_root_node.findall(".//verse")
        if len(prev_verses)>0:
            if "sid" in prev_verses[-1].attrib:
                v_end_xml_node = etree.SubElement(parent_xml_node, "verse")
                v_end_xml_node.set('eid', prev_verses[-1].get('sid'))
        chap_end_xml_node = etree.SubElement(parent_xml_node, "chapter")
        chap_end_xml_node.set("eid", ref)
    elif node.type == "v":
        prev_verses = xml_root_node.findall(".//verse")
        if len(prev_verses)>0:
            if "sid" in prev_verses[-1].attrib:
                v_end_xml_node = etree.SubElement(parent_xml_node, "verse")
                v_end_xml_node.set('eid', prev_verses[-1].get('sid'))
        verse_num_cap = USFM_LANGUAGE.query("(v (verseNumber) @vnum)").captures(node)[0]
        verse_num = usfm_bytes[verse_num_cap[0].start_byte:
            verse_num_cap[0].end_byte].decode('utf-8')
        v_xml_node = etree.SubElement(parent_xml_node, "verse")
        ref = xml_root_node.findall('.//chapter')[-1].get('sid')+ ":"+ verse_num
        v_xml_node.set('number', verse_num.strip())
        v_xml_node.set('sid', ref.strip())
    elif node.type == "verseText":
        for child in node.children:
            node_2_usx(child, usfm_bytes, parent_xml_node, xml_root_node)
    elif node.type == 'paragraph':
        para_tag_cap = USFM_LANGUAGE.query("(paragraph (_) @para-marker)").captures(node)[0]
        para_marker = para_tag_cap[0].type
        para_xml_node = etree.SubElement(parent_xml_node, "para")
        para_xml_node.set("style", para_marker)
        for child in para_tag_cap[0].children[1:]:
            node_2_usx(child, usfm_bytes, para_xml_node, xml_root_node)
    elif node.type in NOTE_MARKERS:
        tag_node = node.children[0]
        caller_node = node.children[1]
        note_xml_node = etree.SubElement(parent_xml_node, "note")
        note_xml_node.set("style",
            usfm_bytes[tag_node.start_byte:tag_node.end_byte].decode('utf-8')
            .replace("\\","").strip())
        note_xml_node.set("caller",
            usfm_bytes[caller_node.start_byte:caller_node.end_byte].decode('utf-8').strip())
        for child in node.children[2:-1]:
            node_2_usx(child, usfm_bytes, note_xml_node, xml_root_node)
    elif node.type in CHAR_STYLE_MARKERS:
        tag_node = node.children[0]
        closing_node = None
        children_range = len(node.children)
        if node.children[-1].type.startswith('\\'):
            closing_node = node.children[-1]
            children_range = children_range-1
        char_xml_node = etree.SubElement(parent_xml_node, "char")
        char_xml_node.set("style",
            usfm_bytes[tag_node.start_byte:tag_node.end_byte].decode('utf-8')
            .replace("\\","").strip())
        if closing_node is None:
            char_xml_node.set("closed", "false")
        else:
            char_xml_node.set("closed", "true")
        for child in node.children[1:children_range]:
            node_2_usx(child, usfm_bytes, char_xml_node, xml_root_node)
    elif node.type.endswith("Attribute"):
        attrib_name_node= node.children[0]
        attrib_name = usfm_bytes[attrib_name_node.start_byte:attrib_name_node.end_byte] \
            .decode('utf-8').strip()
        if attrib_name == "|":
            attrib_name = DEFAULT_ATTRIB_MAP[node.parent.type]

        attrib_val_cap = USFM_LANGUAGE.query("((attributeValue) @attrib-val)").captures(node)[0]
        attrib_value = usfm_bytes[attrib_val_cap[0].start_byte:attrib_val_cap[0].end_byte] \
            .decode('utf-8').strip()
        parent_xml_node.set(attrib_name, attrib_value)
    elif node.type == 'text':
        text_val = usfm_bytes[node.start_byte:node.end_byte].decode('utf-8').strip()
        siblings = parent_xml_node.findall("./*")
        if len(siblings) > 0:
            siblings[-1].tail = text_val
        else:
            parent_xml_node.text = text_val
    elif node.type == "table":
        table_xml_node = etree.SubElement(parent_xml_node, "table")
        for child in node.children:
            node_2_usx(child, usfm_bytes, table_xml_node, xml_root_node)
    elif node.type == "tr":
        row_xml_node = etree.SubElement(parent_xml_node, "row")
        row_xml_node.set("style", "tr")
        for child in node.children[1:]:
            node_2_usx(child, usfm_bytes, row_xml_node, xml_root_node)
    elif node.type in TABLE_CELL_MARKERS:
        tag_node = node.children[0]
        style = usfm_bytes[tag_node.start_byte:tag_node.end_byte].decode('utf-8')\
        .replace("\\","").strip()
        cell_xml_node = etree.SubElement(parent_xml_node, "cell")
        cell_xml_node.set("style", style)
        if "r" in style:
            cell_xml_node.set("align", "end")
        else:
            cell_xml_node.set("align", "start")
        for child in node.children[1:]:
            node_2_usx(child, usfm_bytes, cell_xml_node, xml_root_node)
    elif  node.type == "milestone":
        # print(node.children)
        ms_name_cap = USFM_LANGUAGE.query('''(
            [(milestoneTag)
             (milestoneStartTag)
             (milestoneEndTag)
             ] @ms-name)''').captures(node)[0]
        style = usfm_bytes[ms_name_cap[0].start_byte:ms_name_cap[0].end_byte].decode('utf-8')\
        .replace("\\","").strip()
        ms_xml_node = etree.SubElement(parent_xml_node, "ms")
        ms_xml_node.set('style', style)
        for child in node.children:
            if child.type.endswith("Attribute"):
                node_2_usx(child, usfm_bytes, ms_xml_node, xml_root_node)
    elif node.type == "esb":
        style = "esb"
        sidebar_xml_node = etree.SubElement(parent_xml_node, "sidebar")
        sidebar_xml_node.set("style", style)
        for child in node.children[1:-1]:
            node_2_usx(child, usfm_bytes, sidebar_xml_node, xml_root_node)
    elif node.type == "cat":
        cat_cap = USFM_LANGUAGE.query('((category) @category)').captures(node)[0]
        category = usfm_bytes[cat_cap[0].start_byte:cat_cap[0].end_byte].decode('utf-8').strip()
        parent_xml_node.set('category', category)
    elif node.type == 'fig':
        fig_xml_node = etree.SubElement(parent_xml_node, "figure")
        fig_xml_node.set("style", 'fig')
        for child in node.children[1:-1]:
            node_2_usx(child, usfm_bytes, fig_xml_node, xml_root_node)
    elif node.type == 'b':
        etree.SubElement(parent_xml_node, "optbreak")
    elif (node.type in PARA_STYLE_MARKERS or
          node.type.replace("\\","").strip() in PARA_STYLE_MARKERS):
        tag_node = node.children[0]
        style = usfm_bytes[tag_node.start_byte:tag_node.end_byte].decode('utf-8')
        if style.startswith('\\'):
            style = style.replace('\\','').strip()
        else:
            style = node.type
        children_range_start = 1
        if len(node.children)>1 and node.children[1].type.startswith("numbered"):
            num_node = node.children[1]
            num = usfm_bytes[num_node.start_byte:num_node.end_byte].decode('utf-8')
            style += num
            children_range_start = 2
        para_xml_node = etree.SubElement(parent_xml_node, "para")
        para_xml_node.set("style", style)
        # caps = USFM_LANGUAGE.query('((text) @inner-text)').captures(node)
        # para_xml_node.text = " ".join([usfm_bytes[txt_cap[0].start_byte:
            # txt_cap[0].end_byte].decode('utf-8').strip()
        #  for txt_cap in caps])
        for child in node.children[children_range_start:]:
            node_2_usx(child, usfm_bytes, para_xml_node, xml_root_node)
    elif node.type.strip() in ["","|"]:
        pass # skip white space nodes
    elif len(node.children)>0:
        for child in node.children:
            node_2_usx(child, usfm_bytes, parent_xml_node, xml_root_node)
    else:
        raise Exception("Encountered unknown element ", str(node))

###########VVVVVVVVV Logics for syntax-tree to dict conversions VVVVVV ##############

def node_2_dict_chapter(chapter_node, usfm_bytes):
    '''extract and format chapter head items'''
    chapter_output = {}
    chapter_data_cap = chapter_data_query.captures(chapter_node)
    for chap_data in chapter_data_cap:
        match chap_data:
            case (node, "chapter-number"):
                chapter_output['chapterNumber'] = usfm_bytes[\
                    node.start_byte:node.end_byte].decode('utf-8').strip()
            case (node, "cl-text"):
                chapter_output['cl'] = usfm_bytes[node.start_byte:
                                    node.end_byte].decode('utf-8').strip()
            case (node, "ca-number"):
                chapter_output['ca'] = usfm_bytes[node.start_byte:
                                    node.end_byte].decode('utf-8').strip()
            case (node, "cp-text"):
                chapter_output['cp'] = usfm_bytes[node.start_byte:
                                    node.end_byte].decode('utf-8').strip()
    return chapter_output


def node_2_dict_verse(verse_node, usfm_bytes):
    '''extract and format verse head items'''
    result = {}
    verse_caps = verse_data_query.captures(verse_node)
    for v_cap in verse_caps:
        match v_cap:
            case (in_node, "verse-number"):
                result['verseNumber'] = usfm_bytes[\
                    in_node.start_byte:in_node.end_byte].decode('utf-8').strip()
            case (in_node, "va-number"):
                result['va'] = usfm_bytes[\
                    in_node.start_byte:in_node.end_byte].decode('utf-8').strip()
            case (in_node, "vp-text"):
                result['vp'] = usfm_bytes[\
                    in_node.start_byte:in_node.end_byte].decode('utf-8').strip()
    return result

def node_2_dict_attrib(attrib_node, usfm_bytes, parent_type):
    '''extract and format attributes and values, also filling out default attributes'''
    val_query = USFM_LANGUAGE.query("((attributeValue) @attrib-val)")
    if attrib_node.type == 'defaultAttribute':
        attrib_name = DEFAULT_ATTRIB_MAP[parent_type]
    elif attrib_node.type == "customAttribute":
        attrib_name_node = USFM_LANGUAGE.query(
            "((customAttributeName) @attr-name)").captures(attrib_node)[0][0]
        attrib_name = usfm_bytes[\
            attrib_name_node.start_byte:attrib_name_node.end_byte].decode('utf-8').strip()
    elif attrib_node.type == "msAttribute":
        attrib_name_node = USFM_LANGUAGE.query(
            "((milestoneAttributeName) @attr-name)").captures(attrib_node)[0][0]
        attrib_name = usfm_bytes[\
            attrib_name_node.start_byte:attrib_name_node.end_byte].decode('utf-8').strip()
    else:
        attrib_name = attrib_node.children[0].type
    val_node = val_query.captures(attrib_node)[0]
    val = usfm_bytes[val_node[0].start_byte:val_node[0].end_byte].decode('utf-8').strip()
    return {attrib_name:val}

def node_2_dict_milestone(ms_node, usfm_bytes):
    '''extract and format milestone nodes'''
    attribs = []
    for child in ms_node.children:
        if child.type.endswith("Tag"):
            ms_name_node = child
        elif child.type.endswith("Attribute"):
            attribs.append(node_2_dict_attrib(child, usfm_bytes, ms_node.type))
    ms_name = usfm_bytes[\
            ms_name_node.start_byte:ms_name_node.end_byte].decode('utf-8').strip().replace("\\","")
    result = {'milestone':ms_name}
    if len(attribs) > 0:
        result['attributes'] = attribs
    return result

def node_2_dict_generic(node, usfm_bytes):
    '''The general rules to cover the common marker types'''
    marker_name = node.type
    content = ""
    tag_node = None
    text_node = None
    closing_node = None
    attribs = []
    for child in node.children:
        if child.type.endswith("Tag"):
            tag_node = child
        elif child.type == "text":
            text_node = child
        elif child.type.strip().startswith('\\') and child.type.strip().endswith("*"):
            closing_node = child
        elif child.type.endswith("Attribute"):
            attribs.append(node_2_dict_attrib(child, usfm_bytes, node.type))
        else:
            inner_cont = node_2_dict_new(child, usfm_bytes)
            if inner_cont is not None:
                content = inner_cont
            # else:
            #     print("igoring:",child)
    if tag_node is not None:
        marker_name = usfm_bytes[\
            tag_node.start_byte:tag_node.end_byte].decode('utf-8').strip().replace("\\","")
    if text_node is not None:
        content = usfm_bytes[text_node.start_byte:text_node.end_byte].decode('utf-8').strip() 
    result = {marker_name:content}
    if len(attribs) > 0:
        result['attributes'] = attribs
    if closing_node is not None:
        result['closing'] = usfm_bytes[\
            closing_node.start_byte:closing_node.end_byte].decode('utf-8').strip()
    return result

def node_2_dict_new(node, usfm_bytes):
    '''recursive function converting a syntax tree node and its children to dictionary'''
    if node.type in ANY_VALID_MARKER:
        return node_2_dict_generic(node, usfm_bytes)
    if node.type.endswith("Block"):
        result = []
        for child in node.children:
            result.append(node_2_dict_new(child, usfm_bytes))
        return result
    if node.type == "paragraph":
        result = {node.children[0].type: []}
        for child in node.children[0].children[1:]:
            result[node.children[0].type].append(node_2_dict_new(child, usfm_bytes))
        return result
    if node.type == "v":
        return node_2_dict_verse(node, usfm_bytes)
    if node.type == 'verseText':
        result = []
        for child in node.children:
            if child.type == "text":
                result.append({'verseText':usfm_bytes[\
                        child.start_byte:child.end_byte].decode('utf-8').strip()})
            else:
                result.append(node_2_dict_new(child,usfm_bytes))
        return result
    if node.type == "list":
        result = {'list':[]}
        for child in node.children:
            result['list'].append(node_2_dict_new(child, usfm_bytes))
        return result
    if node.type == "table":
        result = {"table":[]}
        rows = USFM_LANGUAGE.query("((tr) @row)").captures(node)
        for row in rows:
            cells = []
            for child in row[0].children[1:]:
                cells.append(node_2_dict_new(child, usfm_bytes))
            result['table'].append({"tr":cells})
        return result
    if node.type == "milestone":
        return node_2_dict_milestone(node, usfm_bytes)
    return None

###########^^^^^^^^^^^ Logics for syntax-tree to dict conversions ^^^^^^^^^ ##############


def node_2_dict(node, usfm_bytes):
    '''recursive function converting a syntax tree node and its children to dictionary'''
    if len(node.children)>0:
        item = []
        for child in node.children:
            val = node_2_dict(child, usfm_bytes)
            if child.type == val:
                # pass
                item.append(child.type)
            elif isinstance(val, dict) and len(val)==1 and child.type == list(val.keys())[0]:
                item.append({child.type: val[child.type]})
            else:
                item.append({child.type: val})
    else:
        if node.type == usfm_bytes[node.start_byte:node.end_byte].decode('utf-8'):
            item = node.type
        else:
            item = {node.type:
                    str(usfm_bytes[node.start_byte:node.end_byte], 'utf-8')}
    return item


def get_captured_node(all_captures, key):
    '''Filter out only a specific type of node from query results'''
    matches = []
    for cap in all_captures:
        if cap[1] == key:
            matches.append(cap[0])
    return matches

######## Newly formed queries#############

id_query = USFM_LANGUAGE.query('''(book (id (bookcode) @book-code (description) @desc))''')

chapter_data_query = USFM_LANGUAGE.query('''(c (chapterNumber) @chapter-number)
                                            (cl (text) @cl-text)
                                            (cp (text) @cp-text)
                                            (ca (chapterNumber) @ca-number)''')

verse_data_query = USFM_LANGUAGE.query('''(v (verseNumber) @verse-number)
                                            (vp (text) @vp-text)
                                            (va (verseNumber) @va-number)''')

######### Old queries ############

bookcode_query = USFM_LANGUAGE.query('''(File (book (id (bookcode) @book-code)))''')

chapter_query = USFM_LANGUAGE.query('''(File (chapter) @chapter)''')

chapternum_query = USFM_LANGUAGE.query('''(c (chapterNumber) @chapter-number)''')

versenum_query = USFM_LANGUAGE.query("""(v (verseNumber) @verse)""")

versetext_query = USFM_LANGUAGE.query("""(verseText) @verse-text""")

text_query = USFM_LANGUAGE.query("""(text) @text""")

error_query = USFM_LANGUAGE.query("""(ERROR) @errors""")

notes_query = USFM_LANGUAGE.query('''[(footnote) (crossref)] @note''')

notestext_query = USFM_LANGUAGE.query('''(noteText) @note-text''')

para_query = USFM_LANGUAGE.query("""[(paragraph) (poetry) (table) (list)] @para""")

title_query = USFM_LANGUAGE.query("""(title) @title""")

class USFMParser():
    """Parser class with usfmstring, syntax_tree and methods for JSON convertions"""
    def __init__(self, usfm_string):
        # super(USFMParser, self).__init__()
        self.usfm = usfm_string
        self.usfm_bytes = None
        self.syntax_tree = None
        self.errors = None
        self.warnings = []

        # Some basic sanity checks
        lower_case_book_code = re.compile(r'^\\id ([a-z0-9][a-z][a-z])')
        if re.match(lower_case_book_code, self.usfm):
            self.warnings.append("Found Book Code in lower case")
            found_book_code = re.match(lower_case_book_code, self.usfm).group(1)
            upper_book_code = found_book_code.upper()
            self.usfm = self.usfm.replace(found_book_code, upper_book_code, 1)


        self.usfm_bytes = bytes(self.usfm, "utf8")
        tree = parser.parse(self.usfm_bytes)
        self.syntax_tree = tree.root_node

        # check for errors in the parse tree and raise them
        errors = error_query.captures(self.syntax_tree)
        if len(errors) > 0:
            self.errors = [(f"At {err[0].start_point}", self.usfm_bytes[err[0].start_byte:
                                    err[0].end_byte].decode('utf-8'))
                                    for err in errors]


    def to_syntax_tree(self):
        '''gives the syntax tree from class, as a string'''
        return self.syntax_tree.sexp()

    def to_dict_new(self, filt=None):
        '''Converts syntax tree to dictionary/json and selection of desired type of contents'''
        dict_output = {"book":{}}
        if filt is None or filt == []:
            filt = list(Filter_new)
        try:
            for child in self.syntax_tree.children:
                match child.type:
                    case "book":
                        id_captures = id_query.captures(child)
                        for id_cap in id_captures:
                            match id_cap:
                                case (node, "book-code"):
                                    dict_output['book']['bookCode'] = self.usfm_bytes[\
                                        node.start_byte:node.end_byte].decode('utf-8').strip()
                                case (node, "desc"):
                                    val = self.usfm_bytes[\
                                        node.start_byte:node.end_byte].decode('utf-8').strip()
                                    if val != "":
                                        dict_output['book']['fileDescription'] = val
                    case "chapter":
                        if "chapters" not in dict_output['book']:
                            dict_output['book']['chapters'] = [] 

                        chapter_output = node_2_dict_chapter(child, self.usfm_bytes)

                        chapter_output['contents'] = []
                        for inner_child in child.children:
                            if inner_child.type not in ['chapterNumber','cl','ca','cp','cd','c']:
                                chapter_output['contents'].append(
                                    node_2_dict_new(inner_child, self.usfm_bytes))
                        dict_output['book']['chapters'].append(chapter_output)
                    case _:
                        if "headers" not in dict_output['book']:
                            dict_output['book']['headers'] = []
                        if Filter_new.BOOK_HEADERS in filt:
                            dict_output['book']['headers'].append(
                                node_2_dict_new(child, self.usfm_bytes))
        except Exception as exe:
            raise Exception("Unable to do the conversion. "+\
                "Check for errors in <USFMParser obj>.errors") from exe
        return dict_output


    def to_dict(self, filt=Filter.SCRIPTURE_BCV.value):
        '''Converts the syntax tree from class as a dict in python, convertable to JSON'''
        try:
            if filt in [Filter.SCRIPTURE_BCV.value, Filter.NOTES.value, Filter.NOTES_TEXT.value,
                Filter.SCRIPTURE_PARAGRAPHS.value, None]:
                dict_output = {}
                captures = bookcode_query.captures(self.syntax_tree)
                cap = captures[0]
                dict_output['book'] = {'bookCode': self.usfm_bytes[cap[0].start_byte:
                                        cap[0].end_byte].decode('utf-8')}
                dict_output['book']['chapters'] = []
                captures = chapter_query.captures(self.syntax_tree)
                for cap in captures:
                    chap_captures = chapternum_query.captures(cap[0])
                    ccap= chap_captures[0]
                    dict_output['book']['chapters'].append({"chapterNumber":
                        self.usfm_bytes[ccap[0].start_byte:ccap[0].end_byte].decode('utf-8'),
                        "contents":[]})
                    match filt:
                        case Filter.SCRIPTURE_BCV.value | None:
                            # query for just the chapter, verse and text nodes from the syntax_tree
                            versenum_captures = versenum_query.captures(cap[0])
                            versetext_captures = versetext_query.captures(cap[0])
                            combined = {item[0].start_byte: item for item in\
                                            versenum_captures+versetext_captures}
                            sorted_combined = [combined[i] for i in  sorted(combined)]
                            for vcap in sorted_combined:
                                match vcap:
                                    case (vnode, "verse"):
                                        dict_output['book']['chapters'][-1]["contents"].append(
                                            {"verseNumber":self.usfm_bytes[vnode.start_byte:
                                                vnode.end_byte].decode('utf-8').strip(),
                                             "verseText":""})
                                    case (vnode, "verse-text"):
                                        text_captures = text_query.captures(vnode)
                                        text_val = "".join([self.usfm_bytes[tcap[0].start_byte:
                                                    tcap[0].end_byte].decode('utf-8').replace("\n", " ")
                                                        for tcap in text_captures])
                                        dict_output['book']['chapters'][-1]['contents'][-1]['verseText'] += text_val
                        case Filter.NOTES.value | Filter.NOTES_TEXT.value:
                            # query for just the chapter, verse and text nodes from the syntax_tree
                            versenum_captures = versenum_query.captures(cap[0])
                            notes_captures = notes_query.captures(cap[0])
                            if len(notes_captures) == 0:
                                continue
                            combined = {item[0].start_byte: item for item in versenum_captures+notes_captures}
                            sorted_combined = [combined[i] for i in  sorted(combined)]
                            for index,vcap in enumerate(sorted_combined):
                                if vcap[1] == "verse" and \
                                    index+1 !=len(sorted_combined) and sorted_combined[index+1][1] =="note":
                                    # need to add a verse only if it has notes
                                    dict_output['book']['chapters'][-1]["contents"].append(
                                        {"verseNumber":self.usfm_bytes[vcap[0].start_byte:
                                            vcap[0].end_byte].decode('utf-8').strip(),
                                         "notes":[]})
                                elif vcap[1] == "note":
                                    note_type = vcap[0].type
                                    if filt == Filter.NOTES.value:
                                        note_details = node_2_dict(vcap[0], self.usfm_bytes)
                                    elif filt == Filter.NOTES_TEXT.value:
                                        notetext_captures = notestext_query.captures(vcap[0])
                                        note_details = "|".join([self.usfm_bytes[ncap[0].start_byte:
                                                    ncap[0].end_byte].decode('utf-8').strip().replace("\n","")\
                                                    for ncap in notetext_captures])
                                    dict_output['book']['chapters'][-1]['contents'][-1]['notes'].append(
                                                                {note_type: note_details})
                        case Filter.SCRIPTURE_PARAGRAPHS.value:
                            # titles and section information, paragraph breaks
                            # and also structuring like lists and tables
                            # along with verse text and versenumber details at the lowest level
                            title_captures = title_query.captures(cap[0])
                            para_captures = para_query.captures(cap[0])
                            combined_tit_paras = {item[0].start_byte: item \
                                            for item in title_captures+para_captures}
                            sorted_tit_paras = [combined_tit_paras[i] for i in  sorted(combined_tit_paras)]
                            for comp in sorted_tit_paras:
                                match comp:
                                    case (comp_node, "title"):
                                        text_captures = text_query.captures(comp_node)
                                        title_texts = []
                                        for tcap in text_captures:
                                            title_texts.append(self.usfm_bytes[tcap[0].start_byte:
                                                                    tcap[0].end_byte].decode('utf-8'))
                                        dict_output['book']['chapters'][-1]['contents'].append(
                                            {"title":" ".join(title_texts).strip()})
                                    case (comp_node, "para"):
                                        comp_type = comp_node.type
                                        versenum_captures = versenum_query.captures(comp_node)
                                        versetext_captures = versetext_query.captures(comp_node)
                                        combined = {item[0].start_byte: item \
                                                for item in versenum_captures+versetext_captures}
                                        sorted_combined = [combined[i] for i in  sorted(combined)]
                                        inner_contents = []
                                        for vcap in sorted_combined:
                                            match vcap:
                                                case (vnode, "verse"):
                                                    inner_contents.append(
                                                        {"verseNumber":self.usfm_bytes[vnode.start_byte:
                                                            vnode.end_byte].decode('utf-8').strip(),
                                                         "verseText":""})
                                                case (vnode, "verse-text"):
                                                    text_captures = text_query.captures(vnode)
                                                    text_val = "".join([self.usfm_bytes[tcap[0].start_byte:
                                                            tcap[0].end_byte].decode('utf-8').replace("\n", " ")
                                                                        for tcap in text_captures])
                                                    if len(inner_contents) == 0:
                                                        inner_contents.append({"verseText":""})
                                                    inner_contents[-1]['verseText'] += text_val

                                        dict_output['book']['chapters'][-1]["contents"].append(
                                                                            {comp_type:inner_contents})
            return dict_output
        except Exception as exe:
            raise Exception("Unable to do the conversion. Check for errors in USFMParser.errors")\
                from exe

        if filt == Filter.ALL.value:
            # directly converts the syntax_tree to JSON/dict'''
            return node_2_dict(self.syntax_tree, self.usfm_bytes)
        raise Exception(f"This filter option, {filt}, is yet to be implemeneted")

    def to_list(self, filt=Filter.SCRIPTURE_BCV.value):
        '''uses the toJSON function and converts JSON to CSV'''
        match filt:
            case Filter.SCRIPTURE_BCV.value | None:
                scripture_json = self.to_dict(Filter.SCRIPTURE_BCV.value)
                table_output = [["Book","Chapter","Verse","Text"]]
                book = scripture_json['book']['bookCode']
                for chap in scripture_json['book']['chapters']:
                    chapter = chap['chapterNumber']
                    for verse in chap['contents']:
                        row = [book, chapter, verse['verseNumber'], '"'+verse['verseText']+'"']
                        table_output.append(row)
                return table_output
            case Filter.NOTES.value:
                notes_json = self.to_dict(Filter.NOTES_TEXT.value)
                table_output = [["Book","Chapter","Verse","Type", "Note"]]
                book = notes_json['book']['bookCode']
                for chap in notes_json['book']['chapters']:
                    chapter = chap['chapterNumber']
                    for verse in chap['contents']:
                        v_num = verse['verseNumber']
                        for note in verse['notes']:
                            typ = list(note)[0]
                            row = [book, chapter, v_num, typ, '"'+note[typ]+'"']
                        table_output.append(row)
                return table_output
            case Filter.SCRIPTURE_PARAGRAPHS.value:
                notes_json = self.to_dict(Filter.SCRIPTURE_PARAGRAPHS.value)
                table_output = [["Book","Chapter","Type", "Contents"]]
                book = notes_json['book']['bookCode']
                for chap in notes_json['book']['chapters']:
                    chapter = chap['chapterNumber']
                    for comp in chap['contents']:
                        typ = list(comp)[0]
                        if typ == "title":
                            cont = comp[typ]
                        else:
                            inner_cont = []
                            for inner_comp in comp[typ]:
                                inner_cont += list(inner_comp.values())
                            cont = ' '.join(inner_cont)
                        row = [book, chapter, typ, cont]
                        table_output.append(row)
                return table_output

            case _:
                raise Exception(f"This filter option, {filt}, is yet to be implemeneted")

    def to_markdown(self, filt=Filter.SCRIPTURE_PARAGRAPHS.value):
        '''query for chapter, paragraph, text structure'''
        return "yet to be implemeneted"


    def to_usx(self, filt=Filter.ALL):
        '''convert the syntax_tree to the XML format USX'''
        usx_root = etree.Element("usx")
        usx_root.set("version", "3.0")

        node_2_usx(self.syntax_tree, self.usfm_bytes, usx_root, usx_root)
        return usx_root
