#!/usr/bin/env python3
from shlib import *
import os

PREFIX = os.getenv("USER", None)

def make_parser():
   import argparse
   parser = argparse.ArgumentParser()
   parser.add_argument("-r", "--root", default="origin/master")
   parser.add_argument("-d", "--dry-run", default=False, action="store_true")
   parser.add_argument("-v", "--verbose", default=False, action="store_true")
   parser.add_argument("-o", "--origin", default="origin")

   return parser

def note_lines(commit):
   ret = Run(["git", "notes", "show", commit], "WOE*")
   if ret.status != 0:
      return

   notes = ret.stdout
   for line in notes.splitlines(keepends=False):
      yield line

def is_push_to(note):
   parts = note.split(":")
   return len(parts) == 2 and parts[0] == "push-to"

def push(args, hash, target):
   print(f"pushing to {args.origin} {hash}:refs/heads/{target}")
   ret = Run(["git", "push", f"{args.origin}", "--force-with-lease", f"{hash}:refs/heads/{target}"], "W*")
   assert ret.status == 0, "push failed"

def reset(args, hash, target):
   print(f"reset {target} to {hash}")
   ret = Run(["git", "branch", "-f", target, hash])
   assert ret.status == 0, "reset failed"

def main(argv):
   args = make_parser().parse_args(argv)

   ret = Run(["git", "rev-parse", args.root], "WMO*")
   assert ret.status == 0, "root must be a valid reference"

   ret = Run(["git", "rev-list", "HEAD", "^"+args.root], "WMO*")
   assert ret.status == 0, "failed to retrieve commit list"
   commits = ret.stdout.splitlines(keepends=False)

   ret = Run(["git", "branch", "--show-current"], "WMO*")
   assert ret.status == 0, "could not determine current branch"
   cur_branch_name = ret.stdout.strip()

   if not commits:
      print(f"no valid commits found, try it yourself: git rev-list HEAD ^{args.root}")
      return

   if args.verbose:
      print("considering commits", *commits, sep='\n')
   for hash in commits:
      for note in (n for n in note_lines(hash) if is_push_to(n)):
         parts = note.split(":")
         if args.dry_run:
            print(f"would push: {hash} -> {parts[1]}")
         else:
            push(args, hash, parts[1])
            if parts[1] != cur_branch_name:
               reset(args, hash, parts[1])

if __name__ == '__main__':
   import sys
   main(sys.argv[1:])
