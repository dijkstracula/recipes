#!/usr/bin/env python3
from collections import defaultdict
import glob
import re
from string import Template

name_to_fn = {}
source_to_names = defaultdict(list)
tag_to_names = defaultdict(list)

NAME_MATCHER = r"#\s*([^#]+.*)$"
SOURCE_MATCHER = r"Source:\s*(.*)$"
TAGS_MATCHER = r"Tags:\s*(.*)$"

template = """
= Recipes

Here are some tasty things 2 eat.

== By name:

$byname

== By tag:

$bytag

== By source:

$bysource

"""

def extract_metadata(fn):
    name = source = None
    tags = []
    with open(fn) as f:
        for line in f:
            line = line.strip()
            m = re.match(NAME_MATCHER, line)
            if m is not None:
                name = m.group(1)
            m = re.match(SOURCE_MATCHER, line)
            if m is not None:
                source = m.group(1)
            m = re.match(TAGS_MATCHER, line)
            if m is not None:
                tags = re.split(r",\s*", m.group(1))
    if not name:
        print("{} missing name".format(fn))
    if not source:
        print("{} missing source".format(fn))
    if not tags:
        print("{} missing tags".format(fn))

    return name, source, tags


def walk_repo():
    for fn in glob.glob("*.md", recursive=True):
        if fn == "readme.md":
            continue

        name, source, tags = extract_metadata(fn)
        name_to_fn[name] = fn
        source_to_names[source.lower()].append(name)
        for tag in tags:
            tag_to_names[tag.lower()].append(name)

def hyperlink(name, path):
    return "[{}]({})".format(name, path)

def dict_to_links(d):
    ret = []
    for key in sorted(d.keys()):
        path = d[key]
        ret.append(hyperlink(key,path) + "\n")
    return "\n".join(ret)

def joined_to_link(outer, inner):
    ret = []
    for key in sorted(outer.keys()):
        ret.append("## {}".format(key) + "\n")
        for value in outer[key]:
            path = inner[value]
            ret.append(hyperlink(value, path) + "\n")
    return "\n".join(ret)

def write_readme():
    byname = dict_to_links(name_to_fn)
    bysource = joined_to_link(source_to_names, name_to_fn)
    bytag = joined_to_link(tag_to_names, name_to_fn)
    with open("readme.md", "w") as f:
        t = Template(template)
        s = t.safe_substitute(byname=byname, bysource=bysource, bytag=bytag)
        f.write(s)

if __name__ == "__main__":
    walk_repo()
    write_readme()
