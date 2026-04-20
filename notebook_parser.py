#!/usr/bin/env python3
"""\
Collection of functions to parse ipynb
"""
import hashlib
import json
from os import PathLike
from pathlib import Path
import re
import sys
from typing import NamedTuple

#Types
type Filepath = str | PathLike[str] | Path
"A filepath that can be converted to a Path object"
type UnprocessedCodeCell = list[str] | str
"Code cell text in jupyter notebook that can be list or string"
type CodeCell = str
"A code cell text in the jupyter notebook"
type CodeCells = list[CodeCell] 
"List of CodeCell (in string)"
type FullPaper = list[CodeCells]
"List of all tasks (with empty `CodeCells` representing missing subtasks)"
class NotebookMetadata(NamedTuple):
    "Metadata found inside the jupyter notebook"
    no_subtask: int
    task_no: int
    paper: str
    hash: str

def get_subtask_from_cell(cell: dict) -> int:
    """
    Attempt to get the subtask number for the cell, return 0 if not found.
    `cell` must be the cell before it is processed (i.e. still with the metadata)
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

def flatten_cell(cell: UnprocessedCodeCell) -> CodeCell:
    "Flatten a cell from str or list[str] into str"
    if isinstance(cell, str):
        return cell
    return '\n'.join(cell)

def get_notebook_metadata(nb: dict) -> NotebookMetadata:
    "Return NotebookMetadata from raw notebook json object"
    try:
        no_subtask = nb['metadata']['nj67']['no_subtask']
        task_no = nb['metadata']['nj67']['task_no']
        paper = nb['metadata']['nj67']['paper']
        hash_str = nb['metadata']['nj67']['hash']
    except KeyError:
        raise NotImplementedError(f"Notebook has missing or insufficient metadata")
    return NotebookMetadata(no_subtask, task_no, paper, hash_str)

def proc_file(file: Filepath) -> CodeCells:
    """
    Return CodeCells ordered by subtask, will raise Exceptions if missing too much metadata.
    """
    with open(Path(file)) as f:
        nb = json.load(f)
    return proc_notebook(nb)

def proc_notebook(nb: dict) -> CodeCells:
    metadata = get_notebook_metadata(nb)
    all_cell_tuples: list[tuple[int, UnprocessedCodeCell]] = [
        (get_subtask_from_cell(cell), cell['source']) 
        for cell in nb['cells'] 
        if cell['cell_type'] == "code"
    ]
    i = 1 # expected subtask of cell, subtassks are 1-indexed
    ordered_cells: CodeCells = []
    for cell_index, cell_tup in enumerate(all_cell_tuples):
        if cell_tup[0] == i:
            ordered_cells.append(flatten_cell(cell_tup[1]))
            i += 1
            continue
        #Ambiguous ordering, will check till EOF or regular ordering found again
        j = 1
        try:
            while True:
                if all_cell_tuples[cell_index + j][0] == i:
                    print(f"Found extra code cell{'s' if j > 1 else ''} after Task {metadata.task_no}.{i-1}, ignoring...", file=sys.stderr)
                    break # back to for loop
                elif all_cell_tuples[cell_index + j][0] == i + j:
                    ordered_cells.append(flatten_cell(cell_tup[1]))
                    print(f"Found code cell with missing task_no metadata, ignoring...", file=sys.stderr)
                    break # back to for loop
                elif all_cell_tuples[cell_index + j][0] in range(i, i+j):
                    raise NotImplementedError(f"Found code cell(s) with missing metadata and ambigous ordering")
                j += 1
            continue
        except IndexError: #End of cells
            print(i, j)
            if i + j - 1 == metadata.no_subtask:
                ordered_cells.extend(map(lambda tup: flatten_cell(tup[1]), all_cell_tuples[i-1:]))
                print("Found cell(s) with missing task_no metadata until EOF, ignoring...")
                break # exit for loop
            raise NotImplementedError(f"Found code cell(s) with missing task_no metadata and ambigous ordering")
    return ordered_cells

def proc_dir(
    dirpath: Filepath, 
    notebooks_filepath: Filepath="nj67-papers/notebooks.json"
) -> dict[str, FullPaper]:
    """
    Return dict of paper name, list of code cells from jupyter notebooks found in dirpath.
    If there is only 1 paper there will only be 1 item in the dict.
    """
    dirpath = Path(dirpath)
    if not dirpath.is_dir():
        raise NotImplementedError(f"'{dirpath}' is not a directory")
    notebooks_info = json.loads(Path(notebooks_filepath).read_text())
    result: dict[str, FullPaper] = {}
    for f in Path(dirpath).iterdir():
        if f.is_file() and f.suffix == '.ipynb':
            nb = json.loads(f.read_text())
            cells = proc_notebook(nb)
            metadata = get_notebook_metadata(nb)
            if metadata.paper in result:
                result[metadata.paper][metadata.task_no-1] = cells
            else:
                try:
                    notebook_info = notebooks_info[metadata.paper]
                    no_subtask = notebook_info['no_task']
                except KeyError:
                    raise NotImplementedError(f"Paper '{metadata.paper} not found or not implemented for checking yet")
                result[metadata.paper] = [[]] * no_subtask
                result[metadata.paper][metadata.task_no-1] = cells
    return result

def proc_single_dir(
    dirpath: Filepath, 
    notebooks_filepath: Filepath="nj67-papers/notebooks.json",
) -> tuple[str, FullPaper]:
    """
    Return a tuple of (paper_name, Fullpaper), or None if no valid notebooks found.
    Like proc_dir, but only process 1 paper and raise errors if more than 1.
    """
    res = proc_dir(dirpath=dirpath, notebooks_filepath=notebooks_filepath)
    if len(res) > 1:
        raise NotImplementedError(f"More than 1 paper found in the directory '{dirpath}'")
    if len(res) == 0:
        raise NotADirectoryError(f"No valid papers found in the directory '{dirpath}'")
    return next(iter(res.items()))

def add_notebook_metadata(
    filepath: Filepath, 
    output_path:Filepath|None=None, 
    replace_code_cells=True
) -> None:
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
        if replace_code_cells:
            cell['source'] = [f"# Task {task_no}.{i}", "# YOUR CODE HERE"]
    nb['metadata']['nj67']['no_subtask'] = i
    try:
        out = Path(output_path) # type: ignore
    except TypeError:
        print(f"Invalid output path: ", output_path)
        out = fp.with_stem(fp.stem + '_processed')
    with out.open('w') as f:
        json.dump(nb, f, indent=1) # Original notebooks had indent=1

# TODO: Is hash_dict really that useful? If the hash survives means the metadata also survives, right?
def get_hash_dict(
    input_dir:Filepath="./nj67-papers/original", 
    output_path:Filepath="./nj67-papers/notebook-hash-dict.json"
) -> None:
    "Get hash dictionary AFTER the metadata has been added in and with unmodified files and writes it to output_path"
    res = {}
    input_dir = Path(input_dir)
    for d in input_dir.iterdir():
        if not d.is_dir(): continue
        for f in d.iterdir():
            if not f.is_file(): continue
            j = json.loads(f.read_text())
            m: dict = j['metadata']['nj67']
            h = m.pop('hash')
            res[h] = m

    with open(Path(output_path), 'w') as f:
        json.dump(res, f, indent=2)


# get_hash_dict()
# from pprint import pprint; pprint(proc_dir("nj67-papers/original/2CZ_NJC_24"))