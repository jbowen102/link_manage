#!/bin/bash

# pass url as first arg
# pass filename (w/o extension) as second arg

if [[ $# -ne 2 ]]; then
	echo "Need to pass in two arguments: source URL and name for .url link." >&2
	exit 2
fi

URL="${1}"
NAME="${2}"
URL_FILENAME="${NAME// /_}.url" # Replace spaces w/ underscores
# https://stackoverflow.com/questions/19661267/replace-spaces-with-underscores-via-bash

FILEPATH_OUT="$(realpath "${PWD}/${URL_FILENAME}")"
# Check for existence of output file
# Check for both resolvable path and broken symlink # https://unix.stackexchange.com/a/550837
if [[ -e "${FILEPATH_OUT}" ]] || [[ -h "${FILEPATH_OUT}" ]]; then
  printf "\nTarget file ${URL_FILENAME} exists. Overwrite? [Y/N]\n"
  read -p ">" answer
  if [ "${answer}" == "y" -o "${answer}" == "Y" ]; then
    rm "${FILEPATH_OUT}"
  else
    printf "Exiting\n"
    exit 1
  fi
fi

echo "[INTERNET SHORTCUT]" > "${FILEPATH_OUT}"
if [[ $? != 0 ]]; then
	printf "\nSomething went wrong with first echo call\n"
	exit 1
fi
echo "URL=$URL" >> "${FILEPATH_OUT}"
if [[ $? != 0 ]]; then
	printf "\nSomething went wrong with second echo call\n"
	exit 1
fi

printf "\nCreated ${FILEPATH_OUT}\n"

