#!/bin/bash
set -e


assert_identical() {
  if cmp --silent -- "$1" "$2"; then
    echo "files contents are identical"
    return 0
  else
    echo "Error: files differ: $1,$2"
    return 1
  fi
}


temp_dir=$(mktemp -d)
extract_archive="$(pwd)/extract-archive.py"
pushd "$temp_dir"
  echo "void return1() {}" > return1.c
  echo "int return2() { return 2; }" > return2.c
  mkdir other
  echo "int return2Other() { return 2; }" > other/return2.c

  mkdir original_objs
  clang -c return1.c -o original_objs/return1.o
  clang -c return2.c -o original_objs/return2.o
  mkdir original_objs/other
  clang -c other/return2.c -o original_objs/other/return2.o

  find original_objs -name *.o -exec ar -q test_archive.a {} \;

  mkdir extracted
  "$extract_archive" --archive "$(pwd)/test_archive.a" --destination "$(pwd)/extracted"

  assert_identical original_objs/return1.o extracted/return1.o || exit 1
  assert_identical original_objs/return2.o extracted/return2.o || assert_identical original_objs/return2.o extracted/2-return2.o || exit 1
  assert_identical original_objs/other/return2.o extracted/return2.o || assert_identical original_objs/other/return2.o extracted/2-return2.o || exit 1
popd

rm -rf "$temp_dir"




