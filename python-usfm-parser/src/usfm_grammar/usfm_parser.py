'''The core logics of converting the syntax tree to other formats'''

from enum import Enum
from importlib import resources
import re

from tree_sitter import Language, Parser
from lxml import etree


class Filter(str, Enum):
    '''Defines the values of filter options'''
    BOOK_HEADERS = "book-header-introduction-markers"
    PARAGRAPHS = 'paragraphs-quotes-lists-tables'
    TITLES = "sectionheadings"
    SCRIPTURE_TEXT = 'verse-texts'
    NOTES = "footnotes-and-crossrefs"
    ATTRIBUTES = "character-level-attributes"
    MILESTONES = "milestones-namespaces"
    STUDY_BIBLE = "sidebars-extended-contents"

class Format(str, Enum):
    '''Defines the valid values for output formats'''
    JSON = "json"
    CSV = "table"
    ST = "syntax-tree"
    USX = "usx"
    MD = "markdown"

class JSONSchema(str, Enum):
    '''The names of two type of JSON/Dict output formats'''
    NESTED = "nested"
    FLAT = "flat"

lang_file = resources.path('usfm_grammar','my-languages.so')
USFM_LANGUAGE = Language(str(lang_file), 'usfm3')
parser = Parser()
parser.set_language(USFM_LANGUAGE)

LIST_MARKERS = ["lh", "li", "lf", "lim", "litl"]
POETRY_MARKERS = ["q", "qr", "qc", "qa", "qm", "qd"]
PARAGRAPH_MARKERS = ["p","m","po","pr","cls","pmo","pm","pmc","pmr","pi","mi","nb","pc","ph"]

# handled alike by the node_2_usx_generic method
PARA_STYLE_MARKERS = ["ide", "usfm", "h", "toc", "toca", #identification
                    "imt", "is", "ip", "ipi", "im", "imi", "ipq", "imq", "ipr", "iq", "ib",
                    "ili", "iot", "io", "iex", "imte", "ie", # intro
                    "mt", "mte", "cl", "cd", "ms", "mr", "s", "sr", "r", "d", "sp", "sd", #titles
                    "sts", "rem", "lit", "restore", #comments
                    ] + LIST_MARKERS + POETRY_MARKERS


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
DEFAULT_ATTRIB_MAP = {"w":"lemma", "rb":"gloss", "xt":"link-href", "fig":"alt",
                    "xt_standalone":"link-href"}
TABLE_CELL_MARKERS = ["tc", "th", "tcr", "thr"]
MISC_MARKERS = ["fig", "cat", "esb", "b", "ph", "pi"]

# Handled alike by the node_2_dict_generic method
# ANY_VALID_MARKER = PARA_STYLE_MARKERS+NOTE_MARKERS+CHAR_STYLE_MARKERS+\
#                     NESTED_CHAR_STYLE_MARKERS+TABLE_CELL_MARKERS+\
#                     MISC_MARKERS

ANY_VALID_MARKER = PARA_STYLE_MARKERS+NOTE_MARKERS+CHAR_STYLE_MARKERS+\
                    NESTED_CHAR_STYLE_MARKERS+TABLE_CELL_MARKERS+ ["tr"]+\
                    PARAGRAPH_MARKERS+MISC_MARKERS

def node_2_usx_id(node, usfm_bytes,parent_xml_node):
    '''build id node in USX'''
    id_captures = USFM_LANGUAGE.query('''(id (bookcode) @book-code
                                                (description)? @desc)''').captures(node)
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

def node_2_usx_chapter(node, usfm_bytes,parent_xml_node, xml_root_node):
    '''build chapter node in USX'''
    chap_cap = USFM_LANGUAGE.query('''(c (chapterNumber) @chap-num)
                                        (ca (chapterNumber) @alt-num)?
                                        (cp (text) @pub-num)?
                                    ''').captures(node)
    chap_num = usfm_bytes[chap_cap[0][0].start_byte:chap_cap[0][0].end_byte].decode('utf-8')
    chap_ref = parent_xml_node.find("book").attrib['code']+" "+chap_num
    chap_xml_node = etree.SubElement(parent_xml_node, "chapter")
    chap_xml_node.set("number", chap_num)
    chap_xml_node.set("style", "c")
    chap_xml_node.set("sid", chap_ref)
    for tupl in chap_cap:
        if tupl[1] == "alt-num":
            chap_xml_node.set('altnumber',
                usfm_bytes[tupl[0].start_byte:tupl[0].end_byte].decode('utf-8').strip())
        if tupl[1] == "pub-num":
            chap_xml_node.set('pubnumber',
                usfm_bytes[tupl[0].start_byte:tupl[0].end_byte].decode('utf-8').strip())
    for child in node.children:
        node_2_usx(child, usfm_bytes, parent_xml_node, xml_root_node)

    prev_verses = xml_root_node.findall(".//verse")
    if len(prev_verses)>0:
        v_end_xml_node = etree.Element("verse")
        v_end_xml_node.set('eid', prev_verses[-1].get('sid'))
        last_sibbling = parent_xml_node[-1]
        if last_sibbling.tag == "para":
            last_sibbling.append(v_end_xml_node)
        elif last_sibbling.tag == "table":
            rows = list(last_sibbling)
            rows[-1].append(v_end_xml_node)
        else:
            parent_xml_node.append(v_end_xml_node)
    chap_end_xml_node = etree.SubElement(parent_xml_node, "chapter")
    chap_end_xml_node.set("eid", chap_ref)

def find_prev_uncle(parent_xml_node):
    '''To find the ealier sibling of the current parent to attach the verse end node'''
    grand_parent = parent_xml_node.getparent()
    uncle_index = -2
    while True:
        if grand_parent[uncle_index].tag in ["sidebar", "ms"]:
            uncle_index -= 1
        else:
            prev_uncle = grand_parent[uncle_index]
            return prev_uncle
    return None

def node_2_usx_verse(node, usfm_bytes, parent_xml_node, xml_root_node):
    '''build verse node in USX'''
    prev_verses = xml_root_node.findall(".//verse")
    if len(prev_verses)>0 and "sid" in prev_verses[-1].attrib:
        if ''.join(parent_xml_node.itertext()) != "":
            # if there is verse text in this parent
            v_end_xml_node = etree.SubElement(parent_xml_node, "verse")
        else:
            prev_uncle = find_prev_uncle(parent_xml_node)
            if prev_uncle.tag == "para":
                v_end_xml_node = etree.SubElement(prev_uncle, "verse")
            elif prev_uncle.tag == "table":
                rows = list(prev_uncle)
                v_end_xml_node = etree.SubElement(rows[-1], "verse")
            else:
                raise Exception(" prev_uncle is "+str(prev_uncle))
        v_end_xml_node.set('eid', prev_verses[-1].get('sid'))
    verse_num_cap = USFM_LANGUAGE.query('''
                            (v
                                (verseNumber) @vnum
                                (va (verseNumber) @alt)?
                                (vp (text) @vp)?
                            )''').captures(node)
    verse_num = usfm_bytes[verse_num_cap[0][0].start_byte:
        verse_num_cap[0][0].end_byte].decode('utf-8')
    v_xml_node = etree.SubElement(parent_xml_node, "verse")
    for tupl in verse_num_cap:
        if tupl[1] == 'alt':
            alt_num = usfm_bytes[tupl[0].start_byte:tupl[0].end_byte].decode('utf-8')
            v_xml_node.set('altnumber', alt_num)
        elif tupl[1] == 'vp':
            vp_text = usfm_bytes[tupl[0].start_byte:tupl[0].end_byte].decode('utf-8')
            v_xml_node.set('pubnumber', vp_text.strip())
    ref = xml_root_node.findall('.//chapter')[-1].get('sid')+ ":"+ verse_num
    v_xml_node.set('number', verse_num.strip())
    v_xml_node.set('style', "v")
    v_xml_node.set('sid', ref.strip())

def node_2_usx_para(node, usfm_bytes, parent_xml_node, xml_root_node):
    '''build paragraph nodes in USX'''
    if node.children[0].type.endswith('Block'):
        for child in node.children[0].children:
            node_2_usx_para(child, usfm_bytes, parent_xml_node, xml_root_node)
    elif node.type == 'paragraph':
        para_tag_cap = USFM_LANGUAGE.query("(paragraph (_) @para-marker)").captures(node)[0]
        para_marker = para_tag_cap[0].type
        if not para_marker.endswith("Block"):
            para_xml_node = etree.SubElement(parent_xml_node, "para")
            para_xml_node.set("style", para_marker)
            for child in para_tag_cap[0].children[1:]:
                node_2_usx(child, usfm_bytes, para_xml_node, xml_root_node)
    elif node.type in ['pi', "ph"]:
        para_marker = usfm_bytes[node.children[0].start_byte:\
            node.children[0].end_byte].decode('utf-8').replace("\\", "").strip()
        para_xml_node = etree.SubElement(parent_xml_node, "para")
        para_xml_node.set("style", para_marker)
        for child in node.children[1:]:
            node_2_usx(child, usfm_bytes, para_xml_node, xml_root_node)

def node_2_usx_notes(node, usfm_bytes, parent_xml_node, xml_root_node):
    '''build USX nodes for footnotes and corss-refs'''
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

def node_2_usx_char(node, usfm_bytes, parent_xml_node, xml_root_node):
    '''build USX nodes for character markups, both regular and nested'''
    tag_node = node.children[0]
    closing_node = None
    children_range = len(node.children)
    if node.children[-1].type.startswith('\\'):
        closing_node = node.children[-1]
        children_range = children_range-1
    char_xml_node = etree.SubElement(parent_xml_node, "char")
    char_xml_node.set("style",
        usfm_bytes[tag_node.start_byte:tag_node.end_byte].decode('utf-8')
        .replace("\\","").replace("+","").strip())
    if closing_node is None:
        char_xml_node.set("closed", "false")
    else:
        char_xml_node.set("closed", "true")
    for child in node.children[1:children_range]:
        node_2_usx(child, usfm_bytes, char_xml_node, xml_root_node)

def node_2_usx_attrib(node, usfm_bytes, parent_xml_node):
    '''add attribute values to USX elements'''
    attrib_name_node= node.children[0]
    attrib_name = usfm_bytes[attrib_name_node.start_byte:attrib_name_node.end_byte] \
        .decode('utf-8').strip()
    if attrib_name == "|":
        attrib_name = DEFAULT_ATTRIB_MAP[node.parent.type]
    if attrib_name == "src": # for \fig
        attrib_name = "file"

    attrib_val_cap = USFM_LANGUAGE.query("((attributeValue) @attrib-val)").captures(node)
    if len(attrib_val_cap) > 0:
        attrib_value = usfm_bytes[attrib_val_cap[0][0].start_byte:\
            attrib_val_cap[0][0].end_byte].decode('utf-8').strip()
    else:
        attrib_value = ""
    parent_xml_node.set(attrib_name, attrib_value)

def node_2_usx_table(node, usfm_bytes, parent_xml_node, xml_root_node):
    '''Handle table related components and convert to usx'''
    if node.type == "table":
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

def node_2_usx_milestone(node, usfm_bytes, parent_xml_node, xml_root_node):
    '''create ms node in USX'''
    ms_name_cap = USFM_LANGUAGE.query('''(
        [(milestoneTag)
         (milestoneStartTag)
         (milestoneEndTag)
         (zSpaceTag)
         ] @ms-name)''').captures(node)[0]
    style = usfm_bytes[ms_name_cap[0].start_byte:ms_name_cap[0].end_byte].decode('utf-8')\
    .replace("\\","").strip()
    ms_xml_node = etree.SubElement(parent_xml_node, "ms")
    ms_xml_node.set('style', style)
    for child in node.children:
        if child.type.endswith("Attribute"):
            node_2_usx(child, usfm_bytes, ms_xml_node, xml_root_node)

def node_2_usx_special(node, usfm_bytes, parent_xml_node, xml_root_node):
    '''Build nodes for esb, cat, fig, optbreak in USX'''
    if node.type == "esb":
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

def node_2_usx_generic(node, usfm_bytes, parent_xml_node, xml_root_node):
    '''build nodes for para style markers in USX'''
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
    for child in node.children[children_range_start:]:
        # node_2_usx(child, usfm_bytes, para_xml_node, xml_root_node)
        if child.type in CHAR_STYLE_MARKERS+NESTED_CHAR_STYLE_MARKERS+\
        ["text", "footnote", "crossref", "verseText", "v", "b", "milestone", "zNameSpace"]:
        # only nest these types inside the upper para style node
            node_2_usx(child, usfm_bytes, para_xml_node, xml_root_node)
        else:
            node_2_usx(child, usfm_bytes, parent_xml_node, xml_root_node)

def node_2_usx(node, usfm_bytes, parent_xml_node, xml_root_node): # pylint: disable= too-many-branches
    '''check each node and based on the type convert to corresponding xml element'''
    # print("working with node: ", node, "\n")
    if node.type == "id":
        node_2_usx_id(node, usfm_bytes, parent_xml_node)
    elif node.type == "chapter":
        node_2_usx_chapter(node, usfm_bytes,parent_xml_node, xml_root_node)
    elif node.type in ["c", "ca", "cp"]:
        pass
    elif node.type == "v":
        node_2_usx_verse(node, usfm_bytes, parent_xml_node, xml_root_node)
    elif node.type == "verseText":
        for child in node.children:
            node_2_usx(child, usfm_bytes, parent_xml_node, xml_root_node)
    elif node.type in ['paragraph', 'pi', "ph"]:
        node_2_usx_para(node, usfm_bytes, parent_xml_node, xml_root_node)
    elif node.type in NOTE_MARKERS:
        node_2_usx_notes(node, usfm_bytes, parent_xml_node, xml_root_node)
    elif node.type in CHAR_STYLE_MARKERS+NESTED_CHAR_STYLE_MARKERS:
        node_2_usx_char(node, usfm_bytes, parent_xml_node, xml_root_node)
    elif node.type.endswith("Attribute"):
        node_2_usx_attrib(node, usfm_bytes, parent_xml_node)
    elif node.type == 'text':
        text_val = usfm_bytes[node.start_byte:node.end_byte].decode('utf-8').strip()
        siblings = parent_xml_node.findall("./*")
        if len(siblings) > 0:
            siblings[-1].tail = text_val
        else:
            parent_xml_node.text = text_val
    elif node.type in ["table", "tr"]+ TABLE_CELL_MARKERS:
        node_2_usx_table(node, usfm_bytes, parent_xml_node, xml_root_node)
    elif  node.type == "milestone":
        node_2_usx_milestone(node, usfm_bytes, parent_xml_node, xml_root_node)
    elif node.type == "zNameSpace":
        node_2_usx_milestone(node, usfm_bytes, parent_xml_node, xml_root_node)
    elif node.type in ["esb", "cat", "fig", "b"]:
        node_2_usx_special(node, usfm_bytes, parent_xml_node, xml_root_node)
    elif (node.type in PARA_STYLE_MARKERS or
          node.type.replace("\\","").strip() in PARA_STYLE_MARKERS):
        node_2_usx_generic(node, usfm_bytes, parent_xml_node, xml_root_node)
    elif node.type.strip() in ["","|"]:
        pass # skip white space nodes
    elif len(node.children)>0:
        for child in node.children:
            node_2_usx(child, usfm_bytes, parent_xml_node, xml_root_node)
    # else:
    #     raise Exception("Encountered unknown element ", str(node))

###########VVVVVVVVV Logics for syntax-tree to dict conversions VVVVVV ##############
NO_NESTING_MARKERS = ['usfm', 'ide', 'h', 'toc', 'toca',
                        'sts', 'rem', 'restore', 'lit',
                        'iqt', 'ior', 'mr', 'sr', 'r',
                        'v', 'va', 'vp', 'c', 'ca', 'cp', 'cl',
                        'sp', 'd', 'fig', 'jmp', 'cat']


def reduce_nesting(nested_json): # pylint: disable=too-many-nested-blocks, too-many-branches
    '''To convert output from NESTED schema to FLAT. Recursive function'''
    result = []
    if isinstance(nested_json, str):
        return [nested_json]
    if isinstance(nested_json, dict): # pylint: disable=too-many-nested-blocks
        for key_orig in nested_json:
            inner_result = None
            key = re.sub(r'[\d+]+','',key_orig)
            if key in ['closing', 'attributes']:
                continue
            if isinstance(nested_json[key_orig], str):
                inner_result = [nested_json[key_orig]]
            else:
                inner_result =  reduce_nesting(nested_json[key_orig])

            if key in PARAGRAPH_MARKERS+POETRY_MARKERS+LIST_MARKERS+TABLE_CELL_MARKERS:
                result.append({key_orig:None})
                result += inner_result
            elif key in PARA_STYLE_MARKERS+["c", "v", "id"]:
                if inner_result is None:
                    result.append({key_orig:None})
                else:
                    for item in inner_result:
                        if isinstance(item, str):
                            result.append({key_orig:item})
                        else:
                            result.append(item)
            elif key in CHAR_STYLE_MARKERS+NOTE_MARKERS+["milestone"]:
                if inner_result is None:
                    last_index = len(result)
                    result.append({key_orig:inner_result})
                else:
                    for item in inner_result:
                        if isinstance(item, str):
                            last_index = len(result)
                            result.append({key_orig:item})
                        else:
                            result.append(item)
                if 'attributes' in nested_json:
                    result[last_index] = result[last_index] | nested_json['attributes']
                if 'closing' in nested_json:
                    result[last_index]['closing'] = nested_json['closing']
            else:
                if inner_result:
                    if isinstance(inner_result, str):
                        inner_result = [inner_result]
                    result += inner_result
    elif isinstance(nested_json, list):
        for item in nested_json:
            inner_result = reduce_nesting(item)
            if inner_result:
                result += inner_result
    if not result:
        return None
    return result

def node_2_dict_id(book_node, usfm_bytes):
    '''Extract bookcode and desc of id marker'''
    result = {
            "tag":"id",
            "cat":"book",
            }
    id_caps = id_query.captures(book_node)
    for cap in id_caps:
        match cap:
            case (in_node, "book-code"):
                result['bookCode'] = usfm_bytes[\
                    in_node.start_byte:in_node.end_byte].decode('utf-8').strip()
                result['value'] = result['bookCode']
            case (in_node, "desc"):
                val = usfm_bytes[\
                    in_node.start_byte:in_node.end_byte].decode('utf-8').strip()
                if val != "":
                    result['description'] = val
                    result['value'] += " "+ val
    return result


def node_2_dict_chapter(chapter_node, usfm_bytes, current_ref):
    '''extract and format chapter head items'''
    chapter_output = {
                        "tag": "c",
                        "cat":"chapter"
                    }
    chapter_data_cap = chapter_data_query.captures(chapter_node)
    for chap_data in chapter_data_cap:
        match chap_data:
            case (node, "chapter-number"):
                chapter_output['value'] = usfm_bytes[\
                    node.start_byte:node.end_byte].decode('utf-8').strip()
                current_ref[1] = chapter_output['value']
            case (node, "ca-number"):
                chapter_output['altNumber'] = usfm_bytes[node.start_byte:
                                    node.end_byte].decode('utf-8').strip()
            case (node, "cp-text"):
                chapter_output['pubNumber'] = usfm_bytes[node.start_byte:
                                    node.end_byte].decode('utf-8').strip()
    if chapter_node.children:
        chapter_output['children'] = []
    for child in chapter_node.children:
        if child.type in ["ca", "cp", "c"]:
            pass
        else:
            chap_content_obj = node_2_dict3(child, usfm_bytes, current_ref)
            # chap_content_obj['types'].append("chapter-content")
            chapter_output['children'].append(chap_content_obj)
    return chapter_output


def node_2_dict_verse(verse_node, usfm_bytes, current_ref):
    '''extract and format verse head items'''
    resp_json = {
        "tag":"v",
        "cat":"verse"
        }
    verse_caps = verse_data_query.captures(verse_node)
    for v_cap in verse_caps:
        match v_cap:
            case (in_node, "verse-number"):
                resp_json['value'] = usfm_bytes[\
                    in_node.start_byte:in_node.end_byte].decode('utf-8').strip()
                current_ref[2] = resp_json['value']
            case (in_node, "va-number"):
                resp_json['altNumber'] = usfm_bytes[\
                    in_node.start_byte:in_node.end_byte].decode('utf-8').strip()
            case (in_node, "vp-text"):
                resp_json['pubNumber'] = usfm_bytes[\
                    in_node.start_byte:in_node.end_byte].decode('utf-8').strip()
    return resp_json

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
    if len(val_query.captures(attrib_node)) > 0:
        val_node = val_query.captures(attrib_node)[0]
        val = usfm_bytes[val_node[0].start_byte:val_node[0].end_byte].decode('utf-8').strip()
    else:
        val = ""
    return {attrib_name:val}

def node_2_dict_milestone(ms_node, usfm_bytes):
    '''extract and format milestone nodes'''
    resp_json = {"cat": "milestone"}
    attribs = []
    for child in ms_node.children:
        if child.type.endswith("Tag"):
            ms_name_node = child
        elif child.type.endswith("Attribute"):
            attribs.append(node_2_dict_attrib(child, usfm_bytes, ms_node.type))
    ms_name = usfm_bytes[\
            ms_name_node.start_byte:ms_name_node.end_byte].decode('utf-8').strip().replace("\\","")
    resp_json['tag'] = ms_name
    if len(attribs) > 0:
        attrib_dict = {}
        for item in attribs:
            attrib_name = list(item)[0]
            attrib_dict[attrib_name] = item[attrib_name]
        resp_json['attributes'] = attrib_dict
    return resp_json

def node_2_dict_text(text_node, usfm_bytes, current_ref):
    '''process verse-text and note-text nodes'''
    resp_json = {'cat':text_node.type}
    values = []
    contents = []
    for child in text_node.children:
        if child.type == "text":
            text = usfm_bytes[child.start_byte:child.end_byte].decode('utf-8').strip()
            if text != "":
                values.append(text)
        else:
            inner_obj = node_2_dict3(child, usfm_bytes, current_ref)
            inner_obj['cat'] = "inline"
            # inner_obj['types'].append("characterMarker")
            if "children" in inner_obj:
                for nested_obj in inner_obj['children']:
                    nested_obj['cat'] = "inline"
            if "value" in inner_obj:
                values.append(inner_obj['value'])
            contents.append(inner_obj)
    if not values and not contents:
        return None
    resp_json['value'] = " ".join(values)
    if contents:
        resp_json['children'] = contents
    if text_node.type == "verseText":
        resp_json['ref'] = f"{current_ref[0]} {current_ref[1]}:{current_ref[2]}"
    return resp_json

def node_2_dict_para(node, usfm_bytes, current_ref):
    '''To handle paragraphs, poetry, lists and tables'''
    resp_json = {"cat":"text"}
    # resp_json['types'].append(node.type)
    resp_json["children"]=[]
    for child in node.children:
        child_obj = node_2_dict3(child, usfm_bytes, current_ref)
        if "tag" in child_obj:
            # p, m, pr,... lh, lf, tr etc
            child_obj['cat'] = node.type
            if "children" in child_obj:
                # tc, tcr, th, thr etc
                for inner_child in child_obj['children']:
                    if "cat" not in inner_child or inner_child['cat'] is None:
                        inner_child["cat"] = node.type
            resp_json['children'].append(child_obj)
        elif "children" in child_obj:
            for inner_child in child_obj['children']:
                inner_child['cat'] = node.type
                resp_json['children'].append(inner_child)
        else:
            raise Exception(f"Dont know what to do with this text.child: {child_obj}")
    return resp_json

def node_2_dict_title(node, usfm_bytes, current_ref):
    '''Converts title and children to dict'''
    resp_json = {
        "cat":"title", 
        "children":[]
        }
    for child in node.children:
        child_obj = node_2_dict3(child, usfm_bytes, current_ref)
        if child_obj:
            if "tag" in child_obj:
                resp_json['children'].append(child_obj)
            elif "children" in child_obj:
                resp_json['children'] += child_obj['children']
    for child_obj in resp_json['children']:
        if "cat" not in child_obj or child_obj['cat'] is None:
            child_obj['cat'] = "title"
        if "children" in child_obj:
            for grand_child in child_obj['children']:
                if "cat" not in grand_child or grand_child['cat'] is None:
                    grand_child['cat'] = "title"

    return resp_json

def node_2_dict_generic(node, usfm_bytes, current_ref):
    '''The general rules to cover the common marker types'''
    resp_json = {
        "tag":None,
        "cat":None
    }
    marker_name = node.type
    if marker_name in CHAR_STYLE_MARKERS+NESTED_CHAR_STYLE_MARKERS:
        resp_json['cat'] = "inline"
    if "Nested" in marker_name:
        marker_name = "+"+marker_name.replace("Nested", "")
    content = []
    values = []
    attribs = []
    for child in node.children:
        if child.type.endswith("Tag"):
            tag_node = child
            marker_name = usfm_bytes[\
                tag_node.start_byte:tag_node.end_byte].decode('utf-8').strip().replace("\\","")
        elif child.type in ["text", "category", "version"]:
            values.append(usfm_bytes[\
                child.start_byte:child.end_byte].decode('utf-8').strip())
        elif child.type.strip().startswith('\\') and child.type.strip().endswith("*"):
            resp_json['closing'] = True
        elif child.type.endswith("Attribute"):
            attribs.append(node_2_dict_attrib(child, usfm_bytes, node.type))
        else:
            inner_cont = node_2_dict3(child, usfm_bytes, current_ref)
            if inner_cont:
                if inner_cont['cat'] == "inline" and "value" in inner_cont:
                    values.append(inner_cont['value'])
                content.append(inner_cont)
    resp_json['tag'] = marker_name
    if content:
        resp_json['children'] = content
    if values:
        resp_json['value'] = " ".join(values)
    if len(attribs) > 0:
        attrib_dict = {}
        for item in attribs:
            attrib_name = list(item)[0]
            attrib_dict[attrib_name] = item[attrib_name]
        resp_json['attributes'] = attrib_dict
    return resp_json


def node_2_dict3(node, usfm_bytes, current_ref):
    '''Accepts a syntax tree node and returns its JSON.
    Calls same function recursively for child nodes'''
    resp_json = None
    if node.type == "v":
        resp_json = node_2_dict_verse(node, usfm_bytes, current_ref)
    elif node.type in ["verseText", "noteText"]:
        resp_json = node_2_dict_text(node, usfm_bytes, current_ref)
    elif node.type in ["paragraph", "poetry","list", "table"]:
        resp_json = node_2_dict_para(node, usfm_bytes, current_ref)
    elif node.type.endswith("Block"):
        resp_json = {
            "cat":"block",
            "children": []
        }
        for child in node.children:
            child_obj = node_2_dict3(child, usfm_bytes, current_ref)
            if child_obj:
                resp_json['children'].append(child_obj)
    elif node.type in ["footnote", "crossref"]:
        resp_json = {
            "cat": node.type,
            "ref": f"{current_ref[0]} {current_ref[1]}:{current_ref[2]}",
            "children":[]
        }
        for child in node.children:
            child_obj = node_2_dict3(child, usfm_bytes, current_ref)
            if child_obj:
                if child_obj['cat'] != "noteText":
                    child_obj['cat'] = node.type
                resp_json['children'].append(child_obj)
    elif node.type in ANY_VALID_MARKER:
        resp_json = node_2_dict_generic(node, usfm_bytes, current_ref)
    elif node.type =="title":
        resp_json = node_2_dict_title(node, usfm_bytes, current_ref)
    elif node.type in ['milestone', "zNameSpace"]:
        resp_json = node_2_dict_milestone(node, usfm_bytes)
    else:
        if node.children:
            resp_json = {"cat":None}
            resp_json['children'] = []
            for child in node.children:
                child_obj = node_2_dict3(child, usfm_bytes, current_ref)
                if child_obj:
                    resp_json['children'].append(child_obj)
    return resp_json



###########^^^^^^^^^^^ Logics for syntax-tree to dict conversions ^^^^^^^^^ ##############



######## Queries#############

id_query = USFM_LANGUAGE.query('''(book (id (bookcode) @book-code (description) @desc))''')

chapter_data_query = USFM_LANGUAGE.query('''(c (chapterNumber) @chapter-number)
                                            (cl (text) @cl-text)
                                            (cp (text) @cp-text)
                                            (ca (chapterNumber) @ca-number)''')

verse_data_query = USFM_LANGUAGE.query('''(v (verseNumber) @verse-number)
                                            (vp (text) @vp-text)
                                            (va (verseNumber) @va-number)''')

error_query = USFM_LANGUAGE.query("""(ERROR) @errors""")

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


    def to_syntax_tree(self, ignore_errors=False):
        '''gives the syntax tree from class, as a string'''
        if not ignore_errors and self.errors:
            err_str = "\n\t".join([":".join(err) for err in self.errors])
            raise Exception("Errors present:"+\
                f'\n\t{err_str}'+\
                "\nUse ignore_errors=True, to generate output inspite of errors")
        return self.syntax_tree.sexp()

    def to_dict(self, filters=None, ignore_errors=False, output_schema=JSONSchema.NESTED): #pylint: disable=too-many-branches, too-many-locals
        '''Converts syntax tree to dictionary/json and selection of desired type of contents'''
        if (not ignore_errors) and self.errors:
            err_str = "\n\t".join([":".join(err) for err in self.errors])
            raise Exception("Errors present:"+\
                f'\n\t{err_str}'+\
                "\nUse ignore_errors=True, to generate output inspite of errors")
        try:
            dict_output = node_2_dict_id(self.syntax_tree, self.usfm_bytes)
            current_ref = [dict_output['bookCode'],"",""]
            dict_output['children'] = []
            for child in self.syntax_tree.children:
                if child.type == "book":
                    pass
                elif child.type == "chapter":
                    chapter_obj = node_2_dict_chapter(child, self.usfm_bytes, current_ref)
                    dict_output['children'].append(chapter_obj)
                else:
                    header_obj = node_2_dict3(child, self.usfm_bytes, current_ref)
                    if header_obj['cat'] == "block":
                        for obj in header_obj['children']:
                            obj['cat'] = "header"
                    else:
                        header_obj['cat'] = "header"
                    dict_output['children'].append(header_obj)
        except Exception as exe:
            message = "Unable to do the conversion. "
            if self.errors:
                err_str = "\n\t".join([":".join(err) for err in self.errors])
                message += f"Could be due to an error in the USFM\n\t{err_str}"
            raise Exception(message)  from exe
        if output_schema == JSONSchema.FLAT:
            try:
                dict_output = reduce_nesting(dict_output)
            except Exception as exe:
                raise Exception("Error at converting to Flat!") from exe
        return dict_output

    def to_list(self, filters=None, ignore_errors=False): # pylint: disable=too-many-branches, too-many-locals
        '''uses the toJSON function and converts JSON to CSV
        To be re-implemented to work with the flat JSON schema'''
        if not ignore_errors and self.errors:
            err_str = "\n\t".join([":".join(err) for err in self.errors])
            raise Exception("Errors present:"+\
                f'\n\t{err_str}'+\
                "\nUse ignore_errors=True, to generate output inspite of errors")

        def scripture_json_str(json_obj):
            '''convert dict to a string eleganlty to add in list o/p'''
            string = ""
            if isinstance(json_obj, dict):
                if "tag" in json_obj:
                    string += "tag=" + json_obj['tag']
                if "value" in json_obj:
                    string += json_obj['value']
            else:
                strings = []
                for child in json_obj['children']:
                    strings.append(scripture_json(child))
                string = "\n".join(strings)
            return string

        scripture_json = self.to_dict(filters, ignore_errors=ignore_errors)
        table_output = [["Book","Chapter","Verse","Verse-Text","Notes","Milestone","Other"]]
        book = scripture_json['bookCode']
        verse_num = None
        verse_text = ""
        note_text = ""
        ms_text = ""
        other_text = ''
        chapter = ""
        for book_child in scripture_json['children']:
            if book_child['cat'] == "chapter":
                chapter = book_child['value']
                for chap_child in book_child['children']:
                    if chap_child['cat'] == "text":
                        for text_child in chap_child['children']:
                            for grand_child in text_child['children']:
                                if grand_child['cat'] == "verse":
                                    if verse_num is not None:
                                        row = [book, chapter, verse_num,
                                                verse_text,note_text,
                                                ms_text,other_text]
                                        table_output.append(row)
                                    verse_text = ""
                                    note_text = ""
                                    ms_text = ""
                                    other_text = ''
                                    verse_num = grand_child['value']
                                elif grand_child['cat'] == 'verseText':
                                    verse_text += grand_child['value']
                                    if "children" in grand_child:
                                        for little_one in grand_child['children']:
                                            if little_one['cat'] == "milestone":
                                                ms_text += scripture_json_str(little_one) + "\n"
                                            # else:
                                            #      other_text += scripture_json_str(little_one) + "\n"

                                elif grand_child['cat'] == "milestone":
                                    ms_text += scripture_json_str(grand_child) + "\n"
                                elif grand_child["cat"] in ["footnote", "crossref"]:
                                    note_text += scripture_json_str(grand_child)
                                # else:
                                #     other_text += scripture_json_str(grand_child)
                    # else:
                    #     other_text += scripture_json_str(chap_child)
        row = [book, chapter, verse_num,
                verse_text,note_text,
                ms_text,other_text]
        table_output.append(row)
        return table_output

    def to_markdown(self):
        '''query for chapter, paragraph, text structure'''
        return "yet to be implemeneted"


    def to_usx(self, ignore_errors=False):
        '''convert the syntax_tree to the XML format USX'''
        if not ignore_errors and self.errors:
            err_str = "\n\t".join([":".join(err) for err in self.errors])
            raise Exception("Errors present:"+\
                f'\n\t{err_str}'+\
                "\nUse ignore_errors=True, to generate output inspite of errors")


        usx_root = etree.Element("usx")
        usx_root.set("version", "3.0")
        try:
            node_2_usx(self.syntax_tree, self.usfm_bytes, usx_root, usx_root)
        except Exception as exe:
            message = "Unable to do the conversion. "
            if self.errors:
                err_str = "\n\t".join([":".join(err) for err in self.errors])
                message += f"Could be due to an error in the USFM\n\t{err_str}"
            raise Exception(message)  from exe
        return usx_root
