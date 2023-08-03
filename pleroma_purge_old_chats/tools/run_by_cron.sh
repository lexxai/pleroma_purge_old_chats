#!/usr/bin/env sh

wrdir=$(dirname "$(readlink -f "$0")")
file_path=${wrdir}/../.venv/bin/pleroma_purge_old_chats
if [ -x "${file_path}" ];then
 sh -c "${file_path}"
fi
