'''The common methods and objects needed in all tests. To be run before all tests'''
from glob import glob
import re
from lxml import etree
from src.usfm_grammar import USFMParser

TEST_DIR = "../tests"

def initialise_parser(input_usfm_path):
    '''Open and parse the given file'''
    with open(input_usfm_path, 'r', encoding='utf-8') as usfm_file:
        usfm_string = usfm_file.read()
    test_parser = USFMParser(usfm_string)
    return test_parser

def is_valid_usfm(input_usfm_path):
    '''Checks the metadata.xml to see is the USFM is a valid one'''
    if input_usfm_path in pass_fail_override_list:
        match pass_fail_override_list[input_usfm_path]:
            case "pass":
                return True
            case "fail":
                return False
    meta_file_path = input_usfm_path.replace("origin.usfm", "metadata.xml")
    with open(meta_file_path, 'r', encoding='utf-8') as meta_file:
        meta_xml_string = meta_file.read()
        if meta_xml_string.startswith("<?xml "):
            # need to remove the first line containing xml declaration 
            # because it doesn't have version, which is mandatory
            meta_xml_string = meta_xml_string.split("\n", 1)[-1] 
    root = etree.fromstring(meta_xml_string)
    node = root.find("validated")
    if node.text == "fail":
        return False
    return True

def find_all_markers(usfm_path, keep_id=False, keep_number=True):
    '''To use regex pattern and finall markers in the USFM file'''
    with open(usfm_path, "r", encoding="utf-8") as in_usfm_file:
        usfm_str = in_usfm_file.read()
        all_markers_in_input =re.findall(r"\\(([A-Za-z]+)\d*(-[se])?)", usfm_str)
    if keep_number:
        all_markers_in_input = [find[0] for find in all_markers_in_input]
    else:
        all_markers_in_input = [find[1]+find[2] for find in all_markers_in_input]
    all_markers_in_input = list(set(all_markers_in_input))
    if not keep_id:
        all_markers_in_input.remove("id")
    if "esbe" in all_markers_in_input:
        assert "esb" in all_markers_in_input
        all_markers_in_input.remove("esbe")
    return all_markers_in_input

all_usfm_files = glob(f"{TEST_DIR}/*/*/origin.usfm")

doubtful_usfms = [
    # f'{TEST_DIR}/mandatory/v/origin.usfm',
    #     # Is V really a must? Can't we have empty chapter stubs?
    # f'{TEST_DIR}/biblica/BlankLinesWithFigures/origin.usfm',
    #     # the occurs under doesn't have c or b, in the sty file
    #     # https://github.com/ubsicap/usfm/blob/6be0cd1fcedfeac19f354c19791d9f1d66721c5e/sty/usfm.sty#L2975
    #     # the desciption on the metadata.xml doesn;t sound veru confident either
    # f'{TEST_DIR}/specExamples/titles/origin.usfm',
    #     # \mte# is shown as occuring under c, as per sty. This file has it before c
    #     # Also, after a heading(\s etc) shouldn't there be a paragraph marker? Its missing too.
    # f'{TEST_DIR}/specExamples/cross-ref/origin.usfm',
    # f'{TEST_DIR}/special-cases/empty-para/origin.usfm',
    # f'{TEST_DIR}/special-cases/empty-c/origin.usfm',
    # f'{TEST_DIR}/special-cases/sp/origin.usfm',
    # f'{TEST_DIR}/paratextTests/WordlistMarkerMissingFromGlossaryCitationForms/origin.usfm',
    # f'{TEST_DIR}/paratextTests/NestingInCrossReferences/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/missing_verses/origin.usfm',
    #     # excluding temporarily, bacause of \\p expecting a spaceOrline afterwards
    #     # Spec says "the space is needed only when text follows the marker...
    #     # ... Most paragraph or poetic markers (like \p, \m, \q# etc.)...
    #     # ...can be followed immediately by a verse number (\v) on a new line."
    #     # DOESN'T THAT MEAN A LINE IS NEEDED AND "\p\v 1 .." usage is not correct?
    # f'{TEST_DIR}/paratextTests/UnmatchedSidebarStart/origin.usfm',
    # f'{TEST_DIR}/paratextTests/CharStyleNotClosed/origin.usfm',
    # f'{TEST_DIR}/paratextTests/CharStyleCrossesVerseNumber/origin.usfm',
    # f'{TEST_DIR}/paratextTests/NestingInFootnote/origin.usfm',
    # f'{TEST_DIR}/paratextTests/FigureNotClosed/origin.usfm',
    # f'{TEST_DIR}/paratextTests/FootnoteNotClosed/origin.usfm',
    # f'{TEST_DIR}/paratextTests/EmptyMarkers/origin.usfm',
    #     # temporarily excluding
    #     # case of MISSING values not reported as ERROR. 
    #     # Problem with tree-sitter, or the way we use it
    # f'{TEST_DIR}/specExamples/character/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/isa_verse_span/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/isa_footnote/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/tit_extra_space_after_chapter/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/1ch_verse_span/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/usfmBodyTestD/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/esb/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/acts_1_milestone.oldformat/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/nb/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/usfmIntroTest/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/usfm-body-testF/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/out_of_sequence_verses/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/acts_1_milestone/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/luk_quotes/origin.usfm',
    # f'{TEST_DIR}/samples-from-wild/doo43-1/origin.usfm',
    # f'{TEST_DIR}/samples-from-wild/doo43-2/origin.usfm',
    #     # excluding becasue no \p (or other paragraph markers)
    #     # after \s, table, esbe etc
    #     # in most of the above usfmjs cases its \s5 that misses \p after it...
    # f'{TEST_DIR}/special-cases/empty-attributes5/origin.usfm',
    #     # just parking for later as this is a low risk corner case
    #     # the space in \w ...|<space>\w* get parsed as "default-argument" and test passes
    # f'{TEST_DIR}/paratextTests/WordlistMarkerTextEndsInSpaceWithoutGlossary/origin.usfm',
    # f'{TEST_DIR}/paratextTests/WordlistMarkerTextContainsNonWordformingPunctuation/origin.usfm',
    # f'{TEST_DIR}/paratextTests/GlossaryCitationFormContainsNonWordformingPunctuation/origin.usfm',
    # f'{TEST_DIR}/paratextTests/WordlistMarkerTextEndsInSpaceWithGlossary/origin.usfm',
    # f'{TEST_DIR}/paratextTests/WordlistMarkerTextEndsInPunctuation/origin.usfm',
    # f'{TEST_DIR}/paratextTests/GlossaryCitationFormEndsInSpace/origin.usfm',
    # f'{TEST_DIR}/paratextTests/WordlistMarkerKeywordEndsInSpace/origin.usfm',
    # f'{TEST_DIR}/paratextTests/WordlistMarkerKeywordEndsInPunctuation/origin.usfm',
    # f'{TEST_DIR}/paratextTests/GlossaryCitationFormEndsInPunctuation/origin.usfm',
    # f'{TEST_DIR}/paratextTests/WordlistMarkerTextEndsInSpaceAndMissingFromGlossary/origin.usfm',
    # f'{TEST_DIR}/paratextTests/WordlistMarkerKeywordContainsNonWordformingPunctuation/origin.usfm',
    # f'{TEST_DIR}/paratextTests/CharStyleClosedAndReopened/origin.usfm',
    #     # I think it is good to cover these usages also, unless they are wrong USFM! Are they?
    #     # these issues look like paratext specific ways of handling spaces and punctuations
    # f'{TEST_DIR}/paratextTests/CustomAttributesAreValid/origin.usfm',
    # f'{TEST_DIR}/paratextTests/ValidMilestones/origin.usfm',
    # f'{TEST_DIR}/paratextTests/LinkAttributesAreValid/origin.usfm',
    #     # Correct syntaxes "x-name", "qt-s", "link-href", 
    #     # but used are "xname", "qts", "linkhref"
    #     # Looks like a bug while writing the text to file
    # f'{TEST_DIR}/paratextTests/EmptyFigure/origin.usfm',
    #     # Older usage of multiple pipes, of USFM 2.x.
    # f'{TEST_DIR}/paratextTests/MissingColumnInTable/origin.usfm',
    #     # Do we need to check column numbers in tables. What if the UI want merged cells?
    # f'{TEST_DIR}/paratextTests/GlossaryCitationFormContainingWordMedialPunctuation_Pass/'
    #     'origin.usfm',
    #     # uses \ in text before quote('). Probably a bug while writing the text to file
    # f'{TEST_DIR}/paratextTests/NoErrorsPartiallyEmptyBook/origin.usfm',
    # f'{TEST_DIR}/paratextTests/NoErrorsEmptyBook/origin.usfm',
    #     # as per USFM spec makers ide, rem, h etc cannot be empty
    # f'{TEST_DIR}/usfmjsTests/acts-1-20.aligned.crammed.oldformat/origin.usfm',
    #     # \q' without space in between and \zaln-s not closed in two palces each
    # f'{TEST_DIR}/usfmjsTests/45-ACT.ugnt.oldformat/origin.usfm',
    #     # toc used without space and text. \k used as \k-s which doesn't seem to be right!
    # f'{TEST_DIR}/usfmjsTests/gn_headers/origin.usfm',
    #     # as per sty file, \mte# occurs under c. Here given after \mt#. Is that correct usage?
    # f'{TEST_DIR}/usfmjsTests/45-ACT.ugnt/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/acts_8-37-ugnt-footnote/origin.usfm',
    #     # \w used inside footnote without nesting(\+w). Also toc used without space or text
    # f'{TEST_DIR}/usfmjsTests/57-TIT.greek.oldformat/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/57-TIT.greek/origin.usfm',
    # f'{TEST_DIR}/samples-from-wild/UGNT2/origin.usfm',
    # f'{TEST_DIR}/samples-from-wild/UGNT1/origin.usfm',
    #     # toc1 used without text or space
    # f'{TEST_DIR}/usfmjsTests/inline_God/origin.usfm',
    #     # nested marker not closed. Is closing not mandatory?
    # f'{TEST_DIR}/samples-from-wild/doo43-4/origin.usfm',
    #     # () usage in \ior  is shown as \ior (....) \ior* in the spec
    # f'{TEST_DIR}/usfmjsTests/greek_verse_objects/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/tw_words/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/tw_words.oldformat/origin.usfm',
    # f'{TEST_DIR}/usfmjsTests/tw_words_chunk/origin.usfm',
    #     # Are \k-s and \k-e valid usages? Are they milestones?

    ]

doubtful_usxs = [
        ########### Related to USX validation ##############
    f'{TEST_DIR}/advanced/custom-attributes/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/tit_1_12/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/tit1-1_alignment.oldformat/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/mat-4-6.oldformat/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/acts_1_11.aligned.oldformat/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/tit_1_12_new_line/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/tit_1_12.alignment/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/greek_verse_objects/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/acts_1_4.aligned.oldformat/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/tw_words/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/heb1-1_multi_alignment/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/acts_1_4.aligned/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/tit1-1_alignment_strongs/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/57-TIT.partial/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/tit_1_12.alignment.zaln.not.start/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/tit_1_12.alignment.oldformat/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/hebrew_words.oldformat/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/mat-4-6/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/57-TIT.partial.oldformat/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/tw_words_chunk/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/mat-4-6.whitespace/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/tit1-1_alignment/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/tit_1_12.word.not.at.line.start/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/heb-12-27.grc/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/mat-4-6.whitespace.oldformat/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/tw_words.oldformat/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/hebrew_words/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/acts-1-20.aligned.oldformat/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/greek/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/greek.oldformat/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/tit_1_12.oldformat/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/acts-1-20.aligned/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/f10_gen12-2_empty_word/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/acts_1_11.aligned/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/heb1-1_multi_alignment.oldformat/origin.usfm',
    f'{TEST_DIR}/samples-from-wild/alignment/origin.usfm',
        # custom attributes are not supported by USX rnc grammar
        # eg: x-morph, x-tw, x-occurrences etc

    f'{TEST_DIR}/paratextTests/GlossaryCitationFormContainsComma_Pass/origin.usfm',
    f'{TEST_DIR}/paratextTests/WordlistMarkerKeywordWithParentheses_Pass/origin.usfm',
    f'{TEST_DIR}/paratextTests/WordlistMarkerNestedProperNoun_Pass/origin.usfm',
    f'{TEST_DIR}/paratextTests/GlossaryNoKeywordErrors/origin.usfm',
    f'{TEST_DIR}/paratextTests/WordlistMarkerKeywordContainsComma_Pass/origin.usfm',
    f'{TEST_DIR}/paratextTests/GlossaryCitationForm_Pass/origin.usfm',
    f'{TEST_DIR}/paratextTests/WordlistMarkerNestedTwoProperNouns_Pass/origin.usfm',
    f'{TEST_DIR}/paratextTests/WordlistMarkerTextEndsInSpaceGlossaryEntryPresent_Pass/'+\
       'origin.usfm',
    f'{TEST_DIR}/paratextTests/WordlistMarkerKeywordEndsInSpaceGlossaryEntryPresent_Pass/'+\
        'origin.usfm',
    f'{TEST_DIR}/paratextTests/GlossaryCitationFormEndsWithParentheses_Pass/origin.usfm',
    f'{TEST_DIR}/paratextTests/GlossaryCitationFormMultipleWords_Pass/origin.usfm',
    f'{TEST_DIR}/paratextTests/WordlistMarkerWithKeyword_Pass/origin.usfm',
    f'{TEST_DIR}/paratextTests/WordlistMarkerNestedProperNounWithKeyword_Pass/origin.usfm',
        # book code GLO is present in usfm docs(for Gloassary) but not present in the USX grammar

    f'{TEST_DIR}/paratextTests/NoErrorsShort/origin.usfm',
    f'{TEST_DIR}/special-cases/empty-book/origin.usfm',
        # USX grammar expects chapters
        # (It actually expects BookTitles also, but I changed it to optional)

    f'{TEST_DIR}/usfmjsTests/tstudio/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/psa_quotes/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/isa_inline_quotes/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/pro_footnote/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/pro_quotes/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/job_footnote/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/out_of_sequence_chapters/origin.usfm',
        # \s5 not supported by the USX grammar

    f'{TEST_DIR}/usfmjsTests/links/origin.usfm',
        # link-href reported as invalid by usx grammar. Even the doc example doesn't work.

    f'{TEST_DIR}/usfmjsTests/ts/origin.usfm',
    f'{TEST_DIR}/usfmjsTests/ts_2/origin.usfm',
        # qt is a char marker and ts a para marker, as per RNC grammar!

    f'{TEST_DIR}/special-cases/nesting/origin.usfm',
    f'{TEST_DIR}/samples-from-wild/rv3/origin.usfm',
        # nesting of w within other(add) char markers not supported by the USX.rnc grammar

    f'{TEST_DIR}/special-cases/empty-attributes/origin.usfm',
    # f'{TEST_DIR}/samples-from-wild/rv3/origin.usfm', # already in the list for nested \w
    f'{TEST_DIR}/samples-from-wild/rv1/origin.usfm',
    f'{TEST_DIR}/samples-from-wild/rv2/origin.usfm',
        # format of Strong number in \w attribute is checked in rnc grammar.
        # But its wrong in these tests

    f'{TEST_DIR}/samples-from-wild/t4t2/origin.usfm',
        # \b occuring immediately after \s, not within a para
    ]

pass_fail_override_list = {
    # custom attribute without x-
    f"{TEST_DIR}/paratextTests/InvalidAttributes/origin.usfm": "fail",
    f"{TEST_DIR}/paratextTests/InvalidFigureAttributesReported/origin.usfm": "fail",

    # Use of default attribute for non listed marker
    f"{TEST_DIR}/paratextTests/ValidMilestones/origin.usfm": "fail",

    # link attributes used without hyphen
    f"{TEST_DIR}/paratextTests/LinkAttributesAreValid/origin.usfm": "fail",

    # significant space missing after \p , \q, \m
    f"{TEST_DIR}/paratextTests/CustomAttributesAreValid/origin.usfm": "fail",
    f"{TEST_DIR}/paratextTests/NestingInFootnote/origin.usfm": "fail",
    f"{TEST_DIR}/specExamples/cross-ref/origin.usfm": "fail",
    f"{TEST_DIR}/paratextTests/MarkersMissingSpace/origin.usfm": "fail",
    f"{TEST_DIR}/paratextTests/NestingInCrossReferences/origin.usfm": "fail",
    f"{TEST_DIR}/usfmjsTests/acts-1-20.aligned.crammed.oldformat/origin.usfm": "fail",
    f"{TEST_DIR}/special-cases/empty-para/origin.usfm": "fail",

    # No. of columns in table not validated by usfm-grammar
    f"{TEST_DIR}/paratextTests/MissingColumnInTable/origin.usfm": "pass",

    # WordlistMarkerMissingFromGlossaryCitationForms from paratext. Something to do with \k or \w
    f"{TEST_DIR}/paratextTests/WordlistMarkerMissingFromGlossaryCitationForms/origin.usfm": "pass",

    # no content in ide, rem, toc1 etc
    f"{TEST_DIR}/paratextTests/NoErrorsPartiallyEmptyBook/origin.usfm": "fail",
    f"{TEST_DIR}/paratextTests/NoErrorsEmptyBook/origin.usfm": "fail",
    f"{TEST_DIR}/usfmjsTests/57-TIT.greek.oldformat/origin.usfm": "fail",
    f"{TEST_DIR}/usfmjsTests/57-TIT.greek/origin.usfm": "fail",

    # no \p (usually after \s)
    f"{TEST_DIR}/usfmjsTests/usfmBodyTestD/origin.usfm": "fail", # has \s5
    f"{TEST_DIR}/usfmjsTests/missing_verses/origin.usfm": "fail", # has \s5
    f"{TEST_DIR}/usfmjsTests/isa_verse_span/origin.usfm": "fail", # has \s5
    f"{TEST_DIR}/usfmjsTests/isa_footnote/origin.usfm": "fail", # has \s5
    f"{TEST_DIR}/usfmjsTests/tit_extra_space_after_chapter/origin.usfm": "fail", # has \s5
    f"{TEST_DIR}/usfmjsTests/1ch_verse_span/origin.usfm": "fail", # has \s5
    f"{TEST_DIR}/usfmjsTests/acts_1_milestone.oldformat/origin.usfm": "fail", # has \s5
    f"{TEST_DIR}/usfmjsTests/nb/origin.usfm": "fail", 
    f"{TEST_DIR}/usfmjsTests/usfmIntroTest/origin.usfm": "fail",
    f"{TEST_DIR}/usfmjsTests/usfm-body-testF/origin.usfm": "fail",
    f"{TEST_DIR}/usfmjsTests/out_of_sequence_verses/origin.usfm": "fail",
    f"{TEST_DIR}/usfmjsTests/acts_1_milestone/origin.usfm": "fail",
    f"{TEST_DIR}/usfmjsTests/luk_quotes/origin.usfm": "fail",
    f"{TEST_DIR}/biblica/BlankLinesWithFigures/origin.usfm": "fail", #\fig used without \p, only \b

    # \k-s
    f"{TEST_DIR}/usfmjsTests/45-ACT.ugnt.oldformat/origin.usfm": "fail", # also has \toc1 without content

    # no use of nesting (eg: \w within \f) correct usage: usfmjsTests/acts_8-37-ugnt-footnote
    f"{TEST_DIR}/usfmjsTests/45-ACT.ugnt/origin.usfm": "fail", # also has \toc1 without content

    ########### Need to be fixed #######################
    f"{TEST_DIR}/paratextTests/NoErrorsShort/origin.usfm": "pass", # \c is mandatory!
    f"{TEST_DIR}/usfmjsTests/gn_headers/origin.usfm": "fail", # what is the valid position for mte and imt
    f"{TEST_DIR}/biblica/PublishingVersesWithFormatting/origin.usfm": "fail", # bookcode XXA
    f"{TEST_DIR}/usfmjsTests/acts_8-37-ugnt-footnote/origin.usfm": "fail", # no clue why it fails
}

negative_tests = []
for file_path in all_usfm_files:
    if not is_valid_usfm(file_path):
        negative_tests.append(file_path)

exclude_USX_files = [
    f'{TEST_DIR}/specExamples/chapter-verse/origin.usx',
        # ca is added as attribute to cl not chapter node
    f'{TEST_DIR}/specExamples/milestone/origin.usx',
        # Znamespace not represented properly. Even no docs of it on https://ubsicap.github.io/usx
    f'{TEST_DIR}/advanced/table/origin.xml',
        # There is no verse end node at end(in last row of the table)
]
