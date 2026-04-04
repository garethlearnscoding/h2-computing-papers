# nj67-server

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/garethlearnscoding/nj67-server/tree/testing)

H2 Computing Papers!!

This is the server for nj67, the client can be found [here](https://github.com/ffgtfgh53/nj67-client).

Requirements: Python >= 3.10 (Tested with 3.14 on Linux), no external dependencies

## Cloning

Since `nj67-papers` is a submodule, to fully clone this repo we need an additional flag `--recurse-submodules` to tell git to also clone the submodule repo.

The full command looks like this: 
```
git clone --recurse-submodules https://github.com/garethlearnscoding/nj67-server.git
```
Similarly, to pull any update you also need the `--recurse-submodules` flag, like this:
```
git pull --recurse-submodules
```
If you forgot the flag (either from `git clone` or `git pull`), simply run the following command from this project root to initialise and update all submodules.
```
git submodule update --init --recursive
```

If the command fails, there may be a possibility that the `.gitmodules` file was updated. To fix this, run the following command to syncrhonise the submodules with the server
```
git submodule sync
```
It is possible to add the `--recurse-submodules`  flag to `git pull` and `git clone` by default, read the [git submodule documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules) for more info. (TL;DR, run `git config submodule.recurse true`)

## Testcases

Testcases are not to be run using the file itself, rather to be run using unittest in testcases directory

E.g. to run all testcases: 

```
cd ./nj67-papers/testcases
python -m unittest -v
```
The testcases assume that the neccessary code is present in `taskfile_n` where n is the task number.

The code must also be wrapped in a function or class that the testcase can import and run.