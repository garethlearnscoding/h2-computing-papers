#!/usr/bin/env python
"""\
Collection of functions to parse ipynb
"""
import hashlib
import json
import re
import sys

from pathlib import Path
from typing import Any

def get_subtask_from_cell(cell: dict):
    """\
        Attempt to get the subtask number for the cell, returns 0 if not found
    """
    try:
        return cell['metadata']['nj67']["subtask"]
    except KeyError:
        pass
    try:
        tags = cell['metadata']['tags']
        for tag in tags:
            if tag[:4].lower() == 'task':
                try:
                    return int(tag.split('.')[-1])
                except ValueError:
                    continue
    except KeyError:
        pass
    # source can either be single string or list of strings
    try:
        head = cell['source'].split('\n')[0]
    except AttributeError:
        head = cell['source'][0]
    if (task_string := re.match(r"task\s*\d+\.(\d+)", head, re.IGNORECASE)) is not None:
        return int(task_string.group(1))
    return 0

def proc_file(file):
    "Return list of cells ordered by subtask, will raise Exceptions if missing too much metadata"
    with open(file) as f:
        nb = json.load(f)
    try:
        no_subtask = nb['metadata']['nj67']['no_subtask']
        task_no = nb['metadata']['nj67']['task_no']
    except KeyError:
        raise NotImplementedError(f"No metadata found in file: {file}")
    all_cell_tuples = [(get_subtask_from_cell(cell), cell) 
                    for cell in nb['cells'] if cell['cell_type'] == "code"]
    i = 1 # expected subtask of cell, subtassks are 1-indexed
    ordered_cells = []
    for cell_index, cell_tup in enumerate(all_cell_tuples):
        if cell_tup[0] == i:
            ordered_cells.append(cell_tup[1])
            i += 1
            continue
        #Ambiguous ordering, will check till EOF or regular ordering found again
        j = 1
        try:
            while True:
                if all_cell_tuples[cell_index + j][0] == i:
                    print(f"Found extra code cell{'s' if j > 1 else ''} after Task {task_no}.{i-1}, ignoring...", file=sys.stderr)
                    break
                elif all_cell_tuples[cell_index + j][0] == i + j:
                    ordered_cells.append(cell_tup[1])
                    print(f"Found code cell with missing metadata, ignoring...", file=sys.stderr)
                    break
                elif all_cell_tuples[cell_index + j][0] in range(i, i+j):
                    raise NotImplementedError(f"Found code cell(s) with missing metadata and ambigous ordering")
                j += 1
            continue
        except IndexError: #End of cells
            print(i, j)
            if i + j - 1 == no_subtask:
                ordered_cells.extend(map(lambda tup: tup[1], all_cell_tuples[i-1:]))
                print("Found cell(s) with missing metadata until eof, ignoring...")
                break
            raise NotImplementedError(f"Found code cell(s) with missing metadata and ambigous ordering")
    return ordered_cells

def add_notebook_metadata(filepath: Any, output_path:Any=None):
    """\
    Add metadata of subtask number to code cells and task number to notebook itself
    
    Will fail if the name of the ipynb does not follow the format task_n

    Filename will take precedence over existing metadata
    """
    fp = Path(filepath)
    with fp.open() as f:
        nb = json.load(f)
    if 'nj67' not in nb['metadata']:
        nb['metadata']['nj67'] = {}
    if (filename_match := re.match(r"^(.*?)_?TASK_?(\d+)", fp.stem, re.IGNORECASE)):
        nb['metadata']['nj67']['paper'] = filename_match.group(1)
        task_no = int(filename_match.group(2))
        nb['metadata']['nj67']['task_no'] = task_no
    else:
        raise NotImplementedError("Unable to find paper name and task number from file name or metadata")
    nb['metadata']['nj67']['hash'] = hashlib.md5(fp.stem.encode()).hexdigest()
    i = 0
    for cell in nb['cells']: 
        if cell['cell_type'] != "code":
            continue
        i += 1
        if 'metadata' not in cell:
            cell['metadata'] = {}
        cell['metadata']['nj67'] = {"subtask": i}
        new_tag = f"task {task_no}.{i}"
        current_tags = cell['metadata'].get('tags', [])
        if new_tag not in current_tags:
            cell['metadata']['tags'] = [new_tag] + current_tags
        cell['source'] = [f"# Task {task_no}.{i}", "# YOUR CODE HERE"]
    nb['metadata']['nj67']['no_subtask'] = i
    try:
        out = Path(output_path)
    except TypeError:
        print(f"Invalid output path: ", output_path)
        out = fp.with_stem(fp.stem + '_processed')
    with out.open('w') as f:
        json.dump(nb, f, indent=1)

# add_notebook_metadata("task_67.ipynb")
# print(*proc_file("task_67_processed.ipynb"),sep='\n\n')