'''Just to be used durig development'''
import re
import json
from lxml import etree
from src.usfm_grammar import USFMParser

lxml_object = etree.Element('Root')

with open("../schemas/usx.rnc", encoding='utf-8') as f:
    usxrnc_doc  = f.read()
relaxng = etree.RelaxNG.from_rnc_string(usxrnc_doc)

def get_keys(element):
    '''Recursive function to find all keys in the dict output'''
    keys = []
    if isinstance(element, dict):
        keys += list(element.keys())
        for key in element:
            keys += get_keys(element[key])
    elif isinstance(element, list):
        for item in element:
            keys += get_keys(item)
    return keys

def get_styles(element):
    '''Recursive function to traverse all xml nodes and their style attributes'''
    styles = []
    if 'style' in element.attrib:
        styles.append(element.attrib['style'])
    if element.tag in ['figure', 'optbreak']:
        styles.append(element.tag)
    if "altnumber" in element.attrib:
        styles.append("altnumber")
    if "pubnumber" in element.attrib:
        styles.append("pubnumber")
    if "category" in element.attrib:
        styles.append("category")
    if len(element)>0:
        for child in element:
            styles += get_styles(child)
    return styles


def test_a_sample():
    '''Testing during development'''

    input_str = '''
\\id MAT 41MATGNT92.SFM, Good News Translation, June 2003
\\usfm 3.0
\\toc1 The Acts of the Apostles
\\toc2 Acts
\\ip One of these brothers, Joseph, had become...
\\ipr (50.24)
\\c 136
\\qa Aleph
\\s1 God's Love Never Fails
\\q1
\\v 1 \\qac P\\qac*Praise the \\nd Lord\\nd*! He is good.
\\qr God's love never fails \\qs Selah\\qs*
\\q1
\\v 2 Praise the God of all gods.
\\q1 May his glory fill the whole world.
\\b
\\qc Amen! Amen!
\\qd For the director of music. On my stringed instruments.
\\b
\\v 18 God's spirit took control of one of them, Amasai, who later became the commander of “The Thirty,” and he called out,
\\qm1 “David son of Jesse, we are yours!
\\qm1 Success to you and those who help you!
\\qm1 God is on your side.”
\\b
\\m David welcomed them and made them officers in his army.
'''
    test_parser = USFMParser(input_str)
    assert not test_parser.errors, str(test_parser.errors)+"\n"+test_parser.to_syntax_tree()
    print(test_parser.to_syntax_tree())

    print(test_parser.to_dict())
    assert False