#!/bin/bash

# Pass existing (possibly broken) link path first (one to redirect)
# Second arg is the new target (must resolve)
# Use optional -r flag before other args to indicate resultant link target should be relative

if [ $# -lt 2 ] || [ $# -gt 3 ]; then
	echo "\nExpected between 2 and 3 arguments - optional -r flag, existing link path, and new target path." >&2
	exit 2
  # https://stackoverflow.com/questions/18568706/check-number-of-arguments-passed-to-a-bash-script
elif [ $# == 3 ]; then
  if [ "${1}" == "-r" ]; then
    RELATIVE=1
    EXISTING_LINK_PATH="$(realpath $(dirname ${2}))/$(basename ${2})" # might be broken link
    TARGET_PATH="$(realpath ${3})"
    # https://code-maven.com/bash-absolute-path
  else
    echo "\nExpected first of three args to be '-r'." >&2
	  exit 2
  fi
else
  RELATIVE=0
  EXISTING_LINK_PATH="$(realpath $(dirname ${1}))/$(basename ${1})" # might be broken link
  TARGET_PATH="$(realpath ${2})"
  # https://code-maven.com/bash-absolute-path
fi


# Validate input paths
# Check for both resolvable path and broken symlink # https://unix.stackexchange.com/a/550837
if [ -e "${EXISTING_LINK_PATH}" ] || [ -h "${EXISTING_LINK_PATH}" ]; then
	:
else
  echo "Link path cannot be found." >&2
  exit 2
fi
if [ -e "$(realpath ${TARGET_PATH})" ]; then
  # Use real path or else result will depend on directory user is in when calling script.
  :
else
  # echo "New target path invalid." >&2
  echo "New target path invalid: ${TARGET_PATH}" >&2
  exit 2
fi
# if [ "${TARGET_PATH}" == $(realpath "${EXISTING_LINK_PATH}") ]; then
#   echo "Paths lead to same target." >&2
#   exit 2
# fi


SCRIPT_DIR="$(realpath "$(dirname "${0}")")"
python3 <<< "import link_manage.link_update as lu ; lu.replace_link_target('${EXISTING_LINK_PATH}', '${TARGET_PATH}', ${RELATIVE})"
# https://unix.stackexchange.com/questions/533156/using-python-in-a-bash-script
PYTHON_RETURN=$? # gets return value of last command executed.

# Make sure the program ran correctly
if [ ${PYTHON_RETURN} -ne 0 ]; then
	printf "\nSomething went wrong in Python call to link_update.replace_link_target().\n"
	exit 1
fi



# # Check for both resolvable path and broken symlink
# # https://unix.stackexchange.com/a/550837
# ln -snf "${2}" "${1}"
# # Want to use raw paths entered instead of following any symlinks in path

# # https://unix.stackexchange.com/questions/151999/how-to-change-where-a-symlink-points
# # or do it atomically
# # ln -s new_path temp_symlink_name
# # mv -T temp_symlink_name existing_symlink
# # https://unix.stackexchange.com/questions/88824/how-can-i-edit-symlinks
