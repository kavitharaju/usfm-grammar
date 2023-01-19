
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



## 1. minimal

<table><tr><th>Input</th><th>3.x JSON</th></tr><td>     <pre>
\id GEN
\c 1
\p
\v 1 verse one
\v 2 verse two
</pre></td><td><pre>
{
  "tag": "id",
  "cat": "book",
  "bookCode": "GEN",
  "value": "GEN",
  "children": [
    {
      "tag": "c",
      "cat": "chapter",
      "value": "1",
      "children": [
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "verse one",
                  "ref": "GEN 1:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "verse two",
                  "ref": "GEN 1:2"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
</pre></td>
</tr></table>


## 2. header

<table><tr><th>Input</th><th>3.x JSON</th></tr><td>     <pre>
\id MRK The Gospel of Mark
\ide UTF-8
\usfm 3.0
\h Mark
\mt2 The Gospel according to
\mt1 MARK
\is Introduction
\ip \bk The Gospel according 
to Mark\bk* begins with 
the statement...
\c 1
\p
\v 1 the first verse
\v 2 the second verse

</pre></td><td><pre>
{
  "tag": "id",
  "cat": "book",
  "bookCode": "MRK",
  "value": "MRK The Gospel of Mark",
  "description": "The Gospel of Mark",
  "children": [
    {
      "tag": "ide",
      "cat": "header",
      "value": "UTF-8"
    },
    {
      "tag": "usfm",
      "cat": "header",
      "value": "3.0"
    },
    {
      "cat": "block",
      "children": [
        {
          "tag": "h",
          "cat": "header",
          "value": "Mark"
        }
      ]
    },
    {
      "cat": "block",
      "children": [
        {
          "tag": "mt2",
          "cat": "header",
          "value": "The Gospel according to"
        },
        {
          "tag": "mt1",
          "cat": "header",
          "value": "MARK"
        }
      ]
    },
    {
      "cat": "block",
      "children": [
        {
          "tag": "is",
          "cat": "header",
          "value": "Introduction"
        }
      ]
    },
    {
      "tag": "ip",
      "cat": "header",
      "children": [
        {
          "tag": "bk",
          "cat": "inline",
          "closing": true,
          "value": "The Gospel according \nto Mark"
        }
      ],
      "value": "The Gospel according \nto Mark begins with \nthe statement..."
    },
    {
      "tag": "c",
      "cat": "chapter",
      "value": "1",
      "children": [
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "the first verse",
                  "ref": "MRK 1:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "the second verse",
                  "ref": "MRK 1:2"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
</pre></td>
</tr></table>


## 3. multiple-chapters

<table><tr><th>Input</th><th>3.x JSON</th></tr><td>     <pre>
\id GEN
\c 1
\p
\v 1 the first verse
\v 2 the second verse
\c 2
\p
\v 1 the third verse
\v 2 the fourth verse
</pre></td><td><pre>
{
  "tag": "id",
  "cat": "book",
  "bookCode": "GEN",
  "value": "GEN",
  "children": [
    {
      "tag": "c",
      "cat": "chapter",
      "value": "1",
      "children": [
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "the first verse",
                  "ref": "GEN 1:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "the second verse",
                  "ref": "GEN 1:2"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "tag": "c",
      "cat": "chapter",
      "value": "2",
      "children": [
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "the third verse",
                  "ref": "GEN 2:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "the fourth verse",
                  "ref": "GEN 2:2"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
</pre></td>
</tr></table>


## 4. multiple-paragraphs

<table><tr><th>Input</th><th>3.x JSON</th></tr><td>     <pre>
\id JHN
\c 1
\s1 The Preaching of John the Baptist
\r (Matthew 3.1-12; Luke 3.1-18; John 1.19-28)
\p
\v 1 This is the Good News about Jesus Christ, 
the Son of God.
\v 2 It began as the prophet Isaiah had written:
\q1 “God said, ‘I will send my messenger 
ahead of you
\q2 to open the way for you.’
\q1
\v 3 Someone is shouting in the desert,
\q2 ‘Get the road ready for the Lord;
\q2 make a straight path for him to travel!’”
\p
\v 4 So John appeared in the desert, 
baptizing and preaching. 
“Turn away from your sins and be baptized,” 
he told the people, 
“and God will forgive your sins.”

</pre></td><td><pre>
{
  "tag": "id",
  "cat": "book",
  "bookCode": "JHN",
  "value": "JHN",
  "children": [
    {
      "tag": "c",
      "cat": "chapter",
      "value": "1",
      "children": [
        {
          "cat": "title",
          "children": [
            {
              "tag": "s1",
              "cat": "title",
              "children": [
                {
                  "tag": "r",
                  "cat": "title",
                  "value": "(Matthew 3.1-12; Luke 3.1-18; John 1.19-28)"
                }
              ],
              "value": "The Preaching of John the Baptist"
            }
          ]
        },
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "This is the Good News about Jesus Christ, \nthe Son of God.",
                  "ref": "JHN 1:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "It began as the prophet Isaiah had written:",
                  "ref": "JHN 1:2"
                }
              ]
            }
          ]
        },
        {
          "cat": "text",
          "children": [
            {
              "tag": "q1",
              "cat": "poetry",
              "children": [
                {
                  "cat": "verseText",
                  "value": "“God said, ‘I will send my messenger \nahead of you",
                  "ref": "JHN 1:2"
                }
              ]
            },
            {
              "tag": "q2",
              "cat": "poetry",
              "children": [
                {
                  "cat": "verseText",
                  "value": "to open the way for you.’",
                  "ref": "JHN 1:2"
                }
              ]
            },
            {
              "tag": "q1",
              "cat": "poetry",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "3"
                },
                {
                  "cat": "verseText",
                  "value": "Someone is shouting in the desert,",
                  "ref": "JHN 1:3"
                }
              ]
            },
            {
              "tag": "q2",
              "cat": "poetry",
              "children": [
                {
                  "cat": "verseText",
                  "value": "‘Get the road ready for the Lord;",
                  "ref": "JHN 1:3"
                }
              ]
            },
            {
              "tag": "q2",
              "cat": "poetry",
              "children": [
                {
                  "cat": "verseText",
                  "value": "make a straight path for him to travel!’”",
                  "ref": "JHN 1:3"
                }
              ]
            }
          ]
        },
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "4"
                },
                {
                  "cat": "verseText",
                  "value": "So John appeared in the desert, \nbaptizing and preaching. \n“Turn away from your sins and be baptized,” \nhe told the people, \n“and God will forgive your sins.”",
                  "ref": "JHN 1:4"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
</pre></td>
</tr></table>


## 5. section

<table><tr><th>Input</th><th>3.x JSON</th></tr><td>     <pre>
\id GEN
\c 1
\p
\v 1 the first verse
\v 2 the second verse
\s A new section
\p
\v 3 the third verse
\v 4 the fourth verse
</pre></td><td><pre>
{
  "tag": "id",
  "cat": "book",
  "bookCode": "GEN",
  "value": "GEN",
  "children": [
    {
      "tag": "c",
      "cat": "chapter",
      "value": "1",
      "children": [
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "the first verse",
                  "ref": "GEN 1:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "the second verse",
                  "ref": "GEN 1:2"
                }
              ]
            }
          ]
        },
        {
          "cat": "title",
          "children": [
            {
              "tag": "s",
              "cat": "title",
              "value": "A new section"
            }
          ]
        },
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "3"
                },
                {
                  "cat": "verseText",
                  "value": "the third verse",
                  "ref": "GEN 1:3"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "4"
                },
                {
                  "cat": "verseText",
                  "value": "the fourth verse",
                  "ref": "GEN 1:4"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
</pre></td>
</tr></table>


## 6. footnote

<table><tr><th>Input</th><th>3.x JSON</th></tr><td>     <pre>
\id MAT
\c 1
\p
\v 1 the first verse
\v 2 the second verse
\v 3 This is the Good News 
about Jesus Christ, the Son of 
God. \f + \fr 1.1: \ft Some manuscripts 
do not have \fq the Son of God.\f*
\v 4 yet another verse.

</pre></td><td><pre>
{
  "tag": "id",
  "cat": "book",
  "bookCode": "MAT",
  "value": "MAT",
  "children": [
    {
      "tag": "c",
      "cat": "chapter",
      "value": "1",
      "children": [
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "the first verse",
                  "ref": "MAT 1:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "the second verse",
                  "ref": "MAT 1:2"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "3"
                },
                {
                  "cat": "verseText",
                  "value": "This is the Good News \nabout Jesus Christ, the Son of \nGod.",
                  "ref": "MAT 1:3"
                },
                {
                  "cat": "footnote",
                  "ref": "MAT 1:3",
                  "children": [
                    {
                      "tag": "f",
                      "cat": "footnote",
                      "closing": true,
                      "children": [
                        {
                          "tag": "fr",
                          "cat": "inline",
                          "children": [
                            {
                              "cat": "noteText",
                              "value": "1.1:"
                            }
                          ]
                        },
                        {
                          "tag": "ft",
                          "cat": "inline",
                          "children": [
                            {
                              "cat": "noteText",
                              "value": "Some manuscripts \ndo not have"
                            }
                          ]
                        },
                        {
                          "tag": "fq",
                          "cat": "inline",
                          "children": [
                            {
                              "cat": "noteText",
                              "value": "the Son of God."
                            }
                          ]
                        }
                      ]
                    }
                  ]
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "4"
                },
                {
                  "cat": "verseText",
                  "value": "yet another verse.",
                  "ref": "MAT 1:4"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
</pre></td>
</tr></table>


## 7. cross-refs

<table><tr><th>Input</th><th>3.x JSON</th></tr><td>     <pre>
\id MAT
\c 1
\p
\v 1 the first verse
\v 2 the second verse
\v 3 \x - \xo 2.23: \xt Mrk 1.24; 
Luk 2.39; Jhn 1.45.\x*and made 
his home in a town named Nazareth.

</pre></td><td><pre>
{
  "tag": "id",
  "cat": "book",
  "bookCode": "MAT",
  "value": "MAT",
  "children": [
    {
      "tag": "c",
      "cat": "chapter",
      "value": "1",
      "children": [
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "the first verse",
                  "ref": "MAT 1:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "the second verse",
                  "ref": "MAT 1:2"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "3"
                },
                {
                  "cat": "crossref",
                  "ref": "MAT 1:3",
                  "children": [
                    {
                      "tag": "x",
                      "cat": "crossref",
                      "closing": true,
                      "children": [
                        {
                          "tag": "xo",
                          "cat": "inline",
                          "children": [
                            {
                              "cat": "noteText",
                              "value": "2.23:"
                            }
                          ]
                        },
                        {
                          "tag": "xt",
                          "cat": "inline",
                          "children": [
                            {
                              "cat": "noteText",
                              "value": "Mrk 1.24; \nLuk 2.39; Jhn 1.45."
                            }
                          ]
                        }
                      ]
                    }
                  ]
                },
                {
                  "cat": "verseText",
                  "value": "and made \nhis home in a town named Nazareth.",
                  "ref": "MAT 1:3"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
</pre></td>
</tr></table>


## 8. character

<table><tr><th>Input</th><th>3.x JSON</th></tr><td>     <pre>
\id GEN
\c 1
\p
\v 1 the first verse
\v 2 the second verse
\v 15 Tell the Israelites that I, 
the \nd Lord\nd*, the God of their 
ancestors, the God of Abraham, 
Isaac, and Jacob,

</pre></td><td><pre>
{
  "tag": "id",
  "cat": "book",
  "bookCode": "GEN",
  "value": "GEN",
  "children": [
    {
      "tag": "c",
      "cat": "chapter",
      "value": "1",
      "children": [
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "the first verse",
                  "ref": "GEN 1:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "the second verse",
                  "ref": "GEN 1:2"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "15"
                },
                {
                  "cat": "verseText",
                  "value": "Tell the Israelites that I, \nthe Lord , the God of their \nancestors, the God of Abraham, \nIsaac, and Jacob,",
                  "children": [
                    {
                      "tag": "nd",
                      "cat": "inline",
                      "closing": true,
                      "value": "Lord"
                    }
                  ],
                  "ref": "GEN 1:15"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
</pre></td>
</tr></table>


## 9. attributes

<table><tr><th>Input</th><th>3.x JSON</th></tr><td>     <pre>
\id GEN
\c 1
\p
\v 1 the first verse
\v 2 the second verse \w gracious|lemma="grace" \w*
</pre></td><td><pre>
{
  "tag": "id",
  "cat": "book",
  "bookCode": "GEN",
  "value": "GEN",
  "children": [
    {
      "tag": "c",
      "cat": "chapter",
      "value": "1",
      "children": [
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "the first verse",
                  "ref": "GEN 1:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "the second verse gracious",
                  "children": [
                    {
                      "tag": "w",
                      "cat": "inline",
                      "closing": true,
                      "value": "gracious",
                      "attributes": {
                        "lemma": "grace"
                      }
                    }
                  ],
                  "ref": "GEN 1:2"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
</pre></td>
</tr></table>


## 10. header

<table><tr><th>Input</th><th>3.x JSON</th></tr><td>     <pre>
\id MRK 41MRKGNT92.SFM, Good News Translation, June 2003
\h John
\toc1 The Gospel according to John
\toc2 John
\mt2 The Gospel
\mt3 according to
\mt1 JOHN
\ip The two endings to the Gospel, which are enclosed 
in brackets, are regarded as written by someone 
other than the author of \bk Mark\bk*
\iot Outline of Contents
\io1 The beginning of the gospel \ior (1.1-13)\ior*
\io1 Jesus' public ministry in Galilee \ior (1.14–9.50)\ior*
\io1 From Galilee to Jerusalem \ior (10.1-52)\ior*
\c 1
\ms BOOK ONE
\mr (Psalms 1–41)
\p
\v 1 the first verse
\v 2 the second verse

</pre></td><td><pre>
{
  "tag": "id",
  "cat": "book",
  "bookCode": "MRK",
  "value": "MRK 41MRKGNT92.SFM, Good News Translation, June 2003",
  "description": "41MRKGNT92.SFM, Good News Translation, June 2003",
  "children": [
    {
      "cat": "block",
      "children": [
        {
          "tag": "h",
          "cat": "header",
          "value": "John"
        }
      ]
    },
    {
      "cat": "block",
      "children": [
        {
          "tag": "toc1",
          "cat": "header",
          "value": "The Gospel according to John"
        },
        {
          "tag": "toc2",
          "cat": "header",
          "value": "John"
        }
      ]
    },
    {
      "cat": "block",
      "children": [
        {
          "tag": "mt2",
          "cat": "header",
          "value": "The Gospel"
        },
        {
          "tag": "mt3",
          "cat": "header",
          "value": "according to"
        },
        {
          "tag": "mt1",
          "cat": "header",
          "value": "JOHN"
        }
      ]
    },
    {
      "tag": "ip",
      "cat": "header",
      "children": [
        {
          "tag": "bk",
          "cat": "inline",
          "closing": true,
          "value": "Mark"
        }
      ],
      "value": "The two endings to the Gospel, which are enclosed \nin brackets, are regarded as written by someone \nother than the author of Mark "
    },
    {
      "tag": "iot",
      "cat": "header",
      "value": "Outline of Contents"
    },
    {
      "tag": "io1",
      "cat": "header",
      "children": [
        {
          "tag": "ior",
          "cat": "inline",
          "closing": true,
          "value": "(1.1-13)"
        }
      ],
      "value": "The beginning of the gospel (1.1-13)"
    },
    {
      "tag": "io1",
      "cat": "header",
      "children": [
        {
          "tag": "ior",
          "cat": "inline",
          "closing": true,
          "value": "(1.14–9.50)"
        }
      ],
      "value": "Jesus' public ministry in Galilee (1.14–9.50)"
    },
    {
      "tag": "io1",
      "cat": "header",
      "children": [
        {
          "tag": "ior",
          "cat": "inline",
          "closing": true,
          "value": "(10.1-52)"
        }
      ],
      "value": "From Galilee to Jerusalem (10.1-52)"
    },
    {
      "tag": "c",
      "cat": "chapter",
      "value": "1",
      "children": [
        {
          "cat": "title",
          "children": [
            {
              "tag": "ms",
              "cat": "title",
              "children": [
                {
                  "tag": "mr",
                  "cat": "title",
                  "value": "(Psalms 1–41)"
                }
              ],
              "value": "BOOK ONE"
            }
          ]
        },
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "the first verse",
                  "ref": "MRK 1:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "the second verse",
                  "ref": "MRK 1:2"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
</pre></td>
</tr></table>


## 11. nesting

<table><tr><th>Input</th><th>3.x JSON</th></tr><td>     <pre>
\id GEN
\c 1
\p
\v 1 the first verse
\v 2 the second verse
\v 14 That is 
why \bk The Book of the \+nd Lord\+nd*'s 
Battles\bk*speaks of “...the 
town of Waheb in the area of Suphah

</pre></td><td><pre>
{
  "tag": "id",
  "cat": "book",
  "bookCode": "GEN",
  "value": "GEN",
  "children": [
    {
      "tag": "c",
      "cat": "chapter",
      "value": "1",
      "children": [
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "the first verse",
                  "ref": "GEN 1:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "the second verse",
                  "ref": "GEN 1:2"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "14"
                },
                {
                  "cat": "verseText",
                  "value": "That is \nwhy The Book of the Lord 's \nBattles speaks of “...the \ntown of Waheb in the area of Suphah",
                  "children": [
                    {
                      "tag": "bk",
                      "cat": "inline",
                      "closing": true,
                      "children": [
                        {
                          "tag": "+nd",
                          "cat": "inline",
                          "closing": true,
                          "value": "Lord"
                        }
                      ],
                      "value": "The Book of the Lord 's \nBattles"
                    }
                  ],
                  "ref": "GEN 1:14"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
</pre></td>
</tr></table>


## 12. default-attributes

<table><tr><th>Input</th><th>3.x JSON</th></tr><td>     <pre>
\id GEN
\c 1
\p
\v 1 the first verse
\v 2 the second verse
with \w gracious|grace\w*

</pre></td><td><pre>
{
  "tag": "id",
  "cat": "book",
  "bookCode": "GEN",
  "value": "GEN",
  "children": [
    {
      "tag": "c",
      "cat": "chapter",
      "value": "1",
      "children": [
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "the first verse",
                  "ref": "GEN 1:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "the second verse\nwith gracious",
                  "children": [
                    {
                      "tag": "w",
                      "cat": "inline",
                      "closing": true,
                      "value": "gracious",
                      "attributes": {
                        "lemma": "grace"
                      }
                    }
                  ],
                  "ref": "GEN 1:2"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
</pre></td>
</tr></table>


## 13. custom-attributes

<table><tr><th>Input</th><th>3.x JSON</th></tr><td>     <pre>
\id GEN
\c 1
\p
\v 1 the first verse
\v 2 the second verse 
\w gracious|x-myattr="metadata" \w*
\q1 “Someone is shouting in the desert,
\q2 ‘Prepare a road for the Lord;
\q2 make a straight path for him to travel!’ ”
\s \jmp |link-id="article-john_the_baptist"
 \jmp*John the Baptist
\p John is sometimes called...

</pre></td><td><pre>
{
  "tag": "id",
  "cat": "book",
  "bookCode": "GEN",
  "value": "GEN",
  "children": [
    {
      "tag": "c",
      "cat": "chapter",
      "value": "1",
      "children": [
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "the first verse",
                  "ref": "GEN 1:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "the second verse gracious",
                  "children": [
                    {
                      "tag": "w",
                      "cat": "inline",
                      "closing": true,
                      "value": "gracious",
                      "attributes": {
                        "x-myattr": "metadata"
                      }
                    }
                  ],
                  "ref": "GEN 1:2"
                }
              ]
            }
          ]
        },
        {
          "cat": "text",
          "children": [
            {
              "tag": "q1",
              "cat": "poetry",
              "children": [
                {
                  "cat": "verseText",
                  "value": "“Someone is shouting in the desert,",
                  "ref": "GEN 1:2"
                }
              ]
            },
            {
              "tag": "q2",
              "cat": "poetry",
              "children": [
                {
                  "cat": "verseText",
                  "value": "‘Prepare a road for the Lord;",
                  "ref": "GEN 1:2"
                }
              ]
            },
            {
              "tag": "q2",
              "cat": "poetry",
              "children": [
                {
                  "cat": "verseText",
                  "value": "make a straight path for him to travel!’ ”",
                  "ref": "GEN 1:2"
                }
              ]
            }
          ]
        },
        {
          "cat": "title",
          "children": [
            {
              "tag": "s",
              "cat": "title",
              "children": [
                {
                  "tag": "jmp",
                  "cat": "inline",
                  "closing": true,
                  "value": "",
                  "attributes": {
                    "link-id": "article-john_the_baptist"
                  }
                }
              ],
              "value": " John the Baptist"
            }
          ]
        },
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "cat": "verseText",
                  "value": "John is sometimes called...",
                  "ref": "GEN 1:2"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
</pre></td>
</tr></table>


## 14. list

<table><tr><th>Input</th><th>3.x JSON</th></tr><td>     <pre>
\id GEN
\c 1
\p
\v 1 the first verse
\v 2 the second verse
\c 2
\p
\v 1 the third verse
\v 2 the fourth verse
\s1 Administration of the 
Tribes of Israel
\lh
\v 16-22 This is the list of the 
administrators of the tribes of Israel:
\li1 Reuben - Eliezer son of Zichri
\li1 Simeon - Shephatiah son of Maacah
\li1 Levi - Hashabiah son of Kemuel
\lf This was the list of the 
administrators of the tribes of Israel.

</pre></td><td><pre>
{
  "tag": "id",
  "cat": "book",
  "bookCode": "GEN",
  "value": "GEN",
  "children": [
    {
      "tag": "c",
      "cat": "chapter",
      "value": "1",
      "children": [
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "the first verse",
                  "ref": "GEN 1:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "the second verse",
                  "ref": "GEN 1:2"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "tag": "c",
      "cat": "chapter",
      "value": "2",
      "children": [
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "the third verse",
                  "ref": "GEN 2:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "the fourth verse",
                  "ref": "GEN 2:2"
                }
              ]
            }
          ]
        },
        {
          "cat": "title",
          "children": [
            {
              "tag": "s1",
              "cat": "title",
              "value": "Administration of the \nTribes of Israel"
            }
          ]
        },
        {
          "cat": "text",
          "children": [
            {
              "tag": "lh",
              "cat": "list",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "16-22"
                },
                {
                  "cat": "verseText",
                  "value": "This is the list of the \nadministrators of the tribes of Israel:",
                  "ref": "GEN 2:16-22"
                }
              ]
            },
            {
              "tag": "li1",
              "cat": "list",
              "children": [
                {
                  "cat": "verseText",
                  "value": "Reuben - Eliezer son of Zichri",
                  "ref": "GEN 2:16-22"
                }
              ]
            },
            {
              "tag": "li1",
              "cat": "list",
              "children": [
                {
                  "cat": "verseText",
                  "value": "Simeon - Shephatiah son of Maacah",
                  "ref": "GEN 2:16-22"
                }
              ]
            },
            {
              "tag": "li1",
              "cat": "list",
              "children": [
                {
                  "cat": "verseText",
                  "value": "Levi - Hashabiah son of Kemuel",
                  "ref": "GEN 2:16-22"
                }
              ]
            },
            {
              "tag": "lf",
              "cat": "list",
              "children": [
                {
                  "cat": "verseText",
                  "value": "This was the list of the \nadministrators of the tribes of Israel.",
                  "ref": "GEN 2:16-22"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
</pre></td>
</tr></table>


## 15. table

<table><tr><th>Input</th><th>3.x JSON</th></tr><td>     <pre>
\id GEN
\c 1
\p
\v 1 the first verse
\v 2 the second verse
\p
\v 12-83 They presented their 
offerings in the following order:
\tr \th1 Day \th2 Tribe \th3 Leader
\tr \tcr1 1st \tc2 Judah \tc3 Nahshon 
son of Amminadab
\tr \tcr1 2nd \tc2 Issachar \tc3 Nethanel 
son of Zuar
\tr \tcr1 3rd \tc2 Zebulun \tc3 Eliab 
son of Helon

</pre></td><td><pre>
{
  "tag": "id",
  "cat": "book",
  "bookCode": "GEN",
  "value": "GEN",
  "children": [
    {
      "tag": "c",
      "cat": "chapter",
      "value": "1",
      "children": [
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "the first verse",
                  "ref": "GEN 1:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "the second verse",
                  "ref": "GEN 1:2"
                }
              ]
            }
          ]
        },
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "12-83"
                },
                {
                  "cat": "verseText",
                  "value": "They presented their \nofferings in the following order:",
                  "ref": "GEN 1:12-83"
                }
              ]
            }
          ]
        },
        {
          "cat": "text",
          "children": [
            {
              "tag": "tr",
              "cat": "table",
              "children": [
                {
                  "tag": "th1",
                  "cat": "table",
                  "children": [
                    {
                      "cat": "verseText",
                      "value": "Day",
                      "ref": "GEN 1:12-83"
                    }
                  ]
                },
                {
                  "tag": "th2",
                  "cat": "table",
                  "children": [
                    {
                      "cat": "verseText",
                      "value": "Tribe",
                      "ref": "GEN 1:12-83"
                    }
                  ]
                },
                {
                  "tag": "th3",
                  "cat": "table",
                  "children": [
                    {
                      "cat": "verseText",
                      "value": "Leader",
                      "ref": "GEN 1:12-83"
                    }
                  ]
                }
              ]
            },
            {
              "tag": "tr",
              "cat": "table",
              "children": [
                {
                  "tag": "tcr1",
                  "cat": "table",
                  "children": [
                    {
                      "cat": "verseText",
                      "value": "1st",
                      "ref": "GEN 1:12-83"
                    }
                  ]
                },
                {
                  "tag": "tc2",
                  "cat": "table",
                  "children": [
                    {
                      "cat": "verseText",
                      "value": "Judah",
                      "ref": "GEN 1:12-83"
                    }
                  ]
                },
                {
                  "tag": "tc3",
                  "cat": "table",
                  "children": [
                    {
                      "cat": "verseText",
                      "value": "Nahshon \nson of Amminadab",
                      "ref": "GEN 1:12-83"
                    }
                  ]
                }
              ]
            },
            {
              "tag": "tr",
              "cat": "table",
              "children": [
                {
                  "tag": "tcr1",
                  "cat": "table",
                  "children": [
                    {
                      "cat": "verseText",
                      "value": "2nd",
                      "ref": "GEN 1:12-83"
                    }
                  ]
                },
                {
                  "tag": "tc2",
                  "cat": "table",
                  "children": [
                    {
                      "cat": "verseText",
                      "value": "Issachar",
                      "ref": "GEN 1:12-83"
                    }
                  ]
                },
                {
                  "tag": "tc3",
                  "cat": "table",
                  "children": [
                    {
                      "cat": "verseText",
                      "value": "Nethanel \nson of Zuar",
                      "ref": "GEN 1:12-83"
                    }
                  ]
                }
              ]
            },
            {
              "tag": "tr",
              "cat": "table",
              "children": [
                {
                  "tag": "tcr1",
                  "cat": "table",
                  "children": [
                    {
                      "cat": "verseText",
                      "value": "3rd",
                      "ref": "GEN 1:12-83"
                    }
                  ]
                },
                {
                  "tag": "tc2",
                  "cat": "table",
                  "children": [
                    {
                      "cat": "verseText",
                      "value": "Zebulun",
                      "ref": "GEN 1:12-83"
                    }
                  ]
                },
                {
                  "tag": "tc3",
                  "cat": "table",
                  "children": [
                    {
                      "cat": "verseText",
                      "value": "Eliab \nson of Helon",
                      "ref": "GEN 1:12-83"
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
</pre></td>
</tr></table>


## 16. milestones

<table><tr><th>Input</th><th>3.x JSON</th></tr><td>     <pre>
\id GEN
\c 1
\p
\v 1 the first verse
\v 2 the second verse
\v 3
\qt-s |sid="qt_123" who="Pilate" \*
“Are you the king of the Jews?”
\qt-e |eid="qt_123" \*

</pre></td><td><pre>
{
  "tag": "id",
  "cat": "book",
  "bookCode": "GEN",
  "value": "GEN",
  "children": [
    {
      "tag": "c",
      "cat": "chapter",
      "value": "1",
      "children": [
        {
          "cat": "text",
          "children": [
            {
              "tag": "p",
              "cat": "paragraph",
              "children": [
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "1"
                },
                {
                  "cat": "verseText",
                  "value": "the first verse",
                  "ref": "GEN 1:1"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "2"
                },
                {
                  "cat": "verseText",
                  "value": "the second verse",
                  "ref": "GEN 1:2"
                },
                {
                  "tag": "v",
                  "cat": "verse",
                  "value": "3"
                },
                {
                  "cat": "milestone",
                  "tag": "qt-s",
                  "attributes": {
                    "sid": "qt_123",
                    "who": "Pilate"
                  }
                },
                {
                  "cat": "verseText",
                  "value": "“Are you the king of the Jews?”",
                  "ref": "GEN 1:3"
                },
                {
                  "cat": "milestone",
                  "tag": "qt-e",
                  "attributes": {
                    "eid": "qt_123"
                  }
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
</pre></td>
</tr></table>



