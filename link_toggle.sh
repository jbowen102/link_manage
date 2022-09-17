#!/bin/bash

if [[ $# -ne 1 ]];
then
  echo "Expected one argument - symlink to convert to/from relative." >&2
  exit 2
fi

if [[ -e "${1}" ]]; then
  # Not allowed to be broken link because needed calls to readlink and realpath will fail.
	:
elif [[ -h "${1}" ]]; then
  echo "Link broken. Replace link target and retry." >&2
  exit 2
else
  echo "Cannot find link path." >&2
  exit 2
fi

LINK_PATH="$(realpath $(dirname ${1}))/$(basename ${1})"
LINK_TARGET="$(readlink ${1})"
LINK_TARGET_REALPATH="$(realpath ${1})"

# Temporarily switch working directory to script location to call other script
SCRIPT_DIR="$(realpath "$(dirname "${0}")")"
# https://code-maven.com/bash-absolute-path
cd "${SCRIPT_DIR}"
if [[ "${LINK_TARGET}" == "${LINK_TARGET_REALPATH}" ]]; then
  ./link_replace.sh -r "${LINK_PATH}" "${LINK_TARGET_REALPATH}"
else
  ./link_replace.sh "${LINK_PATH}" "${LINK_TARGET_REALPATH}"
fi
REPLACE_LINK_RETURN=$?

cd - > /dev/null # suppress outputs

if [[ ${REPLACE_LINK_RETURN} == 0 ]]; then
	printf "SUCCESS\n"
else
  printf "FAIL: Call to link_replace unsuccessful.\n"
	exit 1
fi
