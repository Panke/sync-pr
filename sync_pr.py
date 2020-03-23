#!/usr/bin/env python3
from shlib import *
import os

PREFIX = os.getenv("USER", None)

def make_parser():
   import argparse
   parser = argparse.ArgumentParser()
   parser.add_argument("-r", "--root", default="development")
   parser.add_argument("-d", "--dry-run", default=False, action="store_true")
   parser.add_argument("-v", "--verbose", default=False, action="store_true")
   parser.add_argument("-p", "--prefix", default=PREFIX)
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
   return len(parts) == 3 and parts[1] == "push-to"

def push(args, hash, target):
   print(f"pushing to {args.origin} {hash}:refs/heads/{target}")
   ret = Run(["git", "push", f"{args.origin}", "--force-with-lease", f"{hash}:refs/heads/{target}"], "W*")
   assert ret.status == 0, "push failed"

def main(argv):
   args = make_parser().parse_args(argv)
   assert args.prefix is not None, "a prefix is required"

   ret = Run(["git", "rev-parse", args.root], "WMO*")
   assert ret.status == 0, "root must be a valid reference"

   ret = Run(["git", "rev-list", "HEAD", "^"+args.root], "WMO*")
   assert ret.status == 0, "failed to retrieve commit list"

   commits = ret.stdout.splitlines(keepends=False)
   if not commits:
      print(f"no valid commits found, try it yourself: git rev-list HEAD ^{args.root}")
      return

   for hash in commits:
      for note in (n for n in note_lines(hash) if is_push_to(n)):
         parts = note.split(":")
         if parts[0] != args.prefix:
            print(f"ignoring {note} for prefix != '{args.prefix}'")
            continue

         if args.dry_run:
            print(f"would push: {hash} -> {parts[2]}")
         else:
            push(args, hash, parts[2])

if __name__ == '__main__':
   import sys
   main(sys.argv[1:])
