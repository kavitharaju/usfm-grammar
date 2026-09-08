'''Inputs a filepath or file contents of the format
\\marker zmyp
\\category versepara
\\description An paragraph marker extension.

or 

\\marker zmyc
\\category char
\\description A character marker extension.
\\attribute x-myattr1

Reads this content and builds a dictionary/json object.
The value of the marker field becomes the key and 
each of the other lines in that block becomes a key-value pair in the value object.
'''
import re

type_map = {
    'para': 'para',
    'header': 'para',
    'title': 'para',
    'introduction': 'para',
    'section': 'para',
    'para': 'para',
    'versepara': 'para',
    'list': 'para',
    'otherpara': 'para',
    'note': 'note',
    'crossreference': 'note',
    'footnote': 'note',
    'char': 'char',
    'introchar': 'char',
    'listchar': 'char',
    'footnotechar': 'char',
    'crossreferencechar': 'char',
    'milestone': 'milestone',
}

replacement_map = {
    'para': 'customPara_',
    'char': 'customChar_',
    'note': 'customNote_',
    'milestone': 'customMS_',
}


line_pattern = re.compile(r'\\([\w\-]+)\s+(.*)')
class ExtensionReader:
    def __init__(self):
        self.lines = []
        self.extensions = {}

    def read_to_object(self,file_content=None, file_path=None):    
        if file_path and file_content is None:
            file_content = open(file_path, 'r', encoding='utf-8').read()
        self.lines = file_content.splitlines()

        current_marker = None
        for line in self.lines:
            line_match = re.match(line_pattern, line)
            if line_match is not None:
                key = line_match.group(1)
                value = line_match.group(2)
                if key == "marker":
                    if value.startswith('z'):
                        self.extensions[value] = {}
                        current_marker = value
                    else:
                        current_marker = None
                elif current_marker is not None:
                    self.extensions[current_marker][key] = value 
            else:
                pass
                # print(f"Line not conforming to pattern:{line}")
        return self.extensions

    def replace_custom_markers(self, usfm_string):
        modified_usfm = usfm_string
        for marker in self.extensions:
            marker_type = type_map[self.extensions[marker]['category']]
            replacement = replacement_map[marker_type]
            # Replace the marker with the replacement prefix followed by the original marker 
            # if the marker is enclosed by a backslash and a space, newline or *
            marker_pattern = re.compile(rf"\\{re.escape(marker)}(?=[^\w\-]|$)")

            modified_usfm = marker_pattern.sub(
                lambda m: f"\\{replacement}{marker}",
                modified_usfm,
            )
        return modified_usfm



