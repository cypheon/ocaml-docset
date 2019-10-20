#!/usr/bin/env python3

import os
import re

from bs4 import BeautifulSoup

TYPE_CONSTRUCTOR = 'Constructor'
TYPE_EXCEPTION   = 'Exception'
TYPE_FIELD       = 'Field'
TYPE_FUNCTION    = 'Function'
TYPE_LIBRARY     = 'Library'
TYPE_MODULE      = 'Module'
TYPE_TYPE        = 'Type'
TYPE_VALUE       = 'Value'

RE_LIBRARY_CHAPTER = re.compile(r'.+The ([^ ]+) library')

def add_index(name, typ, path):
    print(f'{name:32s}  {typ:12s}  {path}')

def contains(node, string):
    for s in node.strings:
        if string in s:
            return True
    return False

def run(filename):
    with open(filename) as fp:
        soup = BeautifulSoup(fp, 'html.parser')
    soup.made_changes = False
    h1 = soup.find('h1')
    if h1 is None:
        print('WARN: no h1: ' + filename)
        return
    h1_content = list(h1.stripped_strings)
    libmatch = RE_LIBRARY_CHAPTER.fullmatch(' '.join(h1_content))
    def anchor(id):
        return filename + '#' + id
    if h1_content[0].startswith('Module'):
        module_name = h1_content[1]
        add_index(module_name, TYPE_MODULE, filename)
        handle_module(filename, module_name, soup)
    elif libmatch is not None:
        libname = libmatch.group(1)
        add_index(libname, TYPE_LIBRARY, anchor(h1['id']))
        handle_library(filename, libname, soup)
    else:
        print('WARN: no module: ' + filename)
        return

RE_LIB_TYPE = re.compile(r'type (?:.+ |)([a-zA-Z_][a-zA-Z0-9_]*)')
RE_LIB_EXN = re.compile(r'exception ([a-zA-Z_][a-zA-Z0-9_]*)(?: of .+|)')

def handle_library(filename, library_name, soup):
    def anchor(id):
        return filename + '#' + id

    next_id = {'id': 0}
    def autoid():
        id, next_id['id'] = next_id['id'], next_id['id'] + 1
        return f'autoid_{id:04x}'
    def getid(element):
        if 'id' not in element.attrs:
            element['id'] = autoid()
        return element['id']

    for pre in soup.find_all('pre'):
        pretext = ' '.join(pre.stripped_strings)
        m_type = RE_LIB_TYPE.fullmatch(pretext)
        if m_type is not None:
            typname = m_type.group(1)
            add_index(typname, TYPE_TYPE, anchor(getid(pre)))
            continue

        m_exn = RE_LIB_EXN.fullmatch(pretext)
        if m_exn is not None:
            exnname = m_exn.group(1)
            add_index(exnname, TYPE_EXCEPTION, anchor(getid(pre)))
            continue

def handle_module(filename, module_name, soup):
    def anchor(id):
        return filename + '#' + id

    for span in soup.find_all('span', id=True):
        spanid = span['id']
        if spanid.startswith('TYPEELT'):
            name = spanid[7:]
            # this can either be a constructor or a record field
            full_code = ' '.join(span.parent.stripped_strings)
            if ':' in full_code:
                add_index(f'{module_name}.{name}', TYPE_FIELD, anchor(spanid))
            else:
                add_index(f'{module_name}.{name}', TYPE_CONSTRUCTOR, anchor(spanid))
        elif spanid.startswith('TYPE'):
            name = spanid[4:]
            add_index(f'{module_name}.{name}', TYPE_TYPE, anchor(spanid))
        elif spanid.startswith('EXCEPTION'):
            name = spanid[9:]
            add_index(f'{module_name}.{name}', TYPE_EXCEPTION, anchor(spanid))
        elif spanid.startswith('VAL'):
            name = spanid[3:]
            if contains(span.parent, '->'):
                valtype = TYPE_FUNCTION
            else:
                valtype = TYPE_VALUE
            add_index(f'{module_name}.{name}', valtype, anchor(spanid))
            # print(list(span.parent.strings))

if __name__ == '__main__':
    import sys
    import traceback
    for filename in sys.argv[1:]:
        try:
            run(filename)
        except:
            traceback.print_exc()
