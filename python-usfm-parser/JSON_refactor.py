''' A script to ananlyse JSON structure changes'''

from glob import glob
import json
from usfm_grammar import USFMParser, JSONSchema

# input_usfm_samples = glob(f"../tests/basic/*/origin.usfm")
input_usfm_samples = ["../tests/basic/minimal/origin.usfm",
"../tests/basic/header/origin.usfm",
"../tests/basic/multiple-chapters/origin.usfm",
"../tests/basic/multiple-paragraphs/origin.usfm",
"../tests/basic/section/origin.usfm",
"../tests/basic/footnote/origin.usfm",
"../tests/basic/cross-refs/origin.usfm",
"../tests/basic/character/origin.usfm",
"../tests/basic/attributes/origin.usfm",

'../tests/advanced/header/origin.usfm',
'../tests/advanced/nesting/origin.usfm',
'../tests/advanced/default-attributes/origin.usfm',
'../tests/advanced/custom-attributes/origin.usfm',
'../tests/advanced/list/origin.usfm',
'../tests/advanced/table/origin.usfm',
'../tests/advanced/milestones/origin.usfm'
 ]



test_cases = ""
for count,file_name in enumerate(input_usfm_samples):
    with open(file_name, 'r', encoding='utf-8') as in_file:
        usfm_str  = in_file.read()
    parser = USFMParser(usfm_str)
    assert not parser.errors
    dict_output = parser.to_dict()
    # flat_output = parser.to_dict(output_schema=JSONSchema.FLAT)
    test_case_template = f'''
## {count+1}. {file_name.split("/")[-2]}

<table><tr><th>Input</th><th>3.x JSON</th></tr><td>     <pre>
{usfm_str}
</pre></td><td><pre>
{json.dumps(dict_output, indent=2, ensure_ascii=False)}
</pre></td>
</tr></table>

'''
    test_cases += test_case_template

md_file_template = f'''
# USFM Grammar JSON for 3.x

We aim to preserve all the information encoded in USFM while making it user (developer)-friendly based on the following principles:
* Use JSON.
* Every marker is represented by a JSON object that consist of a fixed set of keys making the data predictable for users.
* We define abstractions for categoriesing similar markers for creating an intuitive mental model of the data.
* Explicit representation of the marker hierarchy in USFM that is, sometimes, inherent but not obvious.


### Schema overview
Each JSON object would have all or some of the following fields (Note: the names of the these fields are up for discussion):
* **tag**(or marker): USFM marker name to which this JSON object corresponds to.
* **value**:The content of the marker. e.g. `﹛tag:"ide", value:"utf-8"﹜`. A <u>single place</u> to always access the content. This field in the `verseText` object also <u>combines text</u> snippets split across different character markers providing easy access.
* **category*** (or type): An abstraction of USFM markers based on their semantic meaning and usage. [This](#categories) does not introduce any new semantics but makes explicit the implied semantics in the USFM spec. This allows the user to work with far <u>fewer items in their working memory</u> (less than 20 categories vs. 100+ USFM markers).
* **children**: A list of all the marker objects that belong under _this_  object. e.g. `chapter` objects come under `book`, `verse` is a child of `paragraph`, a character marker as child of `verseText`, etc. Unlike start and end markers in USX, <u>nesting (per the spec and usfm.sty) is made obvious by the JSON structure</u> without having to do further processing to detect boundaries.
* **attributes**: The attributes of character, milestone and fig markers, if present. If <u>default attributes</u> (those with only value and no attribute name specified) are used in the USFM their attribute name is explicity provided saving the users from having to figure them out.
* **closing**: Present and set to `true` if a closing marker is present in the USFM. This enables apps to <u>reconstruct a more faithful USFM</u> from the JSON expression.

`category` is the only mandatory field among these. In addtion to the above:
- book object may have a **bookcode** field.
- verse and chapter objects may have **altNumber** and **pubNumber** like in USX.
- verseText may have a **ref**(or id) object summarizing the book-chapter-verse value it falls under.

### Categories
The `category` field may have **one** of the following values (in the indicated hierarchy):
- _book_(or identification): Corresponds to the `id` marker.
    - _header_ : All markers that occur under `id` and before `c`. Not dividing it further as Introduction, bookTitles, etc. to not expose that complexity to users.
    - _chapter_: Corresponds to the `c` marker. This object will also include information on `ca` and `cp`, if present like in USX. Its `children` will be either _title_ or _text_ objects.
        - _title_: Corresponds to markers like `s`, `ms`, `r`, etc. that form parts of a title and occurs under `c`.
        - _text_(or content): The grouping of text containing markers that come under `c`, which are paragraph, list, poetry and table, within which user can find verses, verseText and notes.
            - _paragraph_: Corresponds to markers like `p`, `m`, `pr`, etc.
            - _poetry_: Corresponds to markers like `q`, `qa`, `qm`, etc.
            - _list_: Corresponds to markers like `lh`, `li`, `lm`, `lf`, etc.
            - _table_: Corresponds to markers `tr`, `tc`, `tcr`, `th` and `thr`.
                - ---
                - _verse_: Marker `v` and information on `va` and `vp`, if present like in USX. Its value will be the verse number and not verseText. Grandkids of _text_ objects.
                - _footnote_: Markers like `f`, `fe` and their children. Grandkids of _text_ objects.
                - _crossref_: Markers like `x`, `xe`, `xt` and their children. Grandkids of _text_ objects.
                - _verseText_ and _noteText_: The text content. Note that this is not represented as children of _verse_ rather as children of _paragraph_-like objects in line with how the USFM spec defines it. This allows handling of cases were verse boundaries conficlt with paragraph boundaries.
                    - _inline_(or characterMarker): Markers `bk`, `nd`, `+nd` etc.
- _milestone_: Predefined milestones, custom milestones and znamespaces. This could come as a child of _book_, _chapter_ or even _text_ objects.
- _studyBible_: Corresponds to `esb`-`esbe` pair. Can come as children of _book_ or _chapter_ and can have _title_ and _text_ objects as its children.
- _block_: A grouping of markers to denote a semantic set as per the spec, especially numbered markers. e.g. `mt#`s, `toc#`s, `toca#`s, etc.


{test_cases}

'''

# with open("JSON_refactor.md", "w", encoding='utf-8') as out_file:
#     out_file.write(md_file_template)

# print(md_file_template)
with open("JSON_refactor.md", "w", encoding='utf-8') as md_file:
    md_file.write(md_file_template)