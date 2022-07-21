#!/bin/bash
set -e


assert_one_identical() {

    original_file=$1
    for f in "${@:2}"; do
      if cmp --silent -- "$original_file" "$f"; then
        echo "$original_file and $f are identical"
        return 0
      fi
    done

    echo "Error: No files matched with $original_file. Tried: ${@:2}"
    return 1
}


temp_dir=$(mktemp -d)
extract_archive="$(pwd)/extract-archive.py"
pushd "$temp_dir"
  echo "void return1() {}" > return1.c
  echo "int return2() { return 2; }" > return2.c
  mkdir other
  echo "int return2Other() { return 2; }" > other/return2.c
  mkdir otherother
  echo "int return3OtherOther() { return 2; }" > otherother/return2.c


  mkdir original_objs
  clang -c return1.c -o original_objs/return1.o
  clang -c return2.c -o original_objs/return2.o
  mkdir original_objs/other
  clang -c other/return2.c -o original_objs/other/return2.o
  mkdir original_objs/otherother
  clang -c otherother/return2.c -o original_objs/otherother/return2.o

  find original_objs -name *.o -exec ar -q test_archive.a {} \;

  mkdir extracted
  "$extract_archive" --archive "$(pwd)/test_archive.a" --destination "$(pwd)/extracted"

  assert_one_identical original_objs/return1.o extracted/return1.o || exit 1
  assert_one_identical original_objs/return2.o extracted/return2.o extracted/2-return2.o extracted/3-return2.o || exit 1
  assert_one_identical original_objs/other/return2.o extracted/return2.o extracted/2-return2.o extracted/3-return2.o || exit 1
  assert_one_identical original_objs/otherother/return2.o extracted/return2.o extracted/2-return2.o extracted/3-return2.o || exit 1
popd

rm -rf "$temp_dir"
