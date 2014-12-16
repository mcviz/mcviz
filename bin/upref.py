#! /usr/bin/env python

from git import Repo
from os import chdir, unlink
from os.path import dirname
from contextlib import contextmanager

from commands import getstatusoutput

@contextmanager
def stash_changes(git):
    try:
        print "--Stashing..",
        stashresult = git.stash()
        print stashresult
        saved_changes = stashresult.strip() != "No local changes to save"
        print "--Saved changes?", saved_changes
        yield
    finally:
        if saved_changes:
            print "--Popping stash.."
            git.stash("pop")

def update_references():
    unlink("inputs/pythia01.referencedot")
    getstatusoutput("make inputs/pythia01.referencedot")
    return ["inputs/pythia01.referencedot"]

def main(argv):

    up_one_from_me = dirname(argv[0]) + "/.."
    chdir(up_one_from_me)
    r = Repo(".")
    git = r.git

    original_branch = r.active_branch

    with stash_changes(git):
        print "--Checking out.."
        print git.checkout("uptodate_references")
        print "--Merging.."
        print git.merge("dev")

    print "--Updating references.."
    updated = update_references()

    if updated and r.is_dirty:
        print "--References changed, committing update."
        print git.add("-u", *updated)
        print git.commit("-m", "Updated references")
    else:
        print "--Reference unchanged. Not committing."

    with stash_changes(git):
        print "--Going back to original branch"
        git.checkout(original_branch)

if __name__ == "__main__":
    from sys import argv
    main(argv)
