#!/usr/bin/env bash
# Spencer Butler <dev@tcos.us>
# relative-link-fixer.sh
# Finds and rewrites absolute GitHub URLs to relative repository links with tracking logic.

set -euo pipefail

BATCH_LIMIT=${BATCH_SIZE:-10}
STORE_FILE=${TCOS_STORE:-".tcos-rel-link-store"}
TARGET_ORG="Twin-Cities-Open-Systems"

declare -a TARGET_FILES

while IFS= read -r -d '' file; do
    if grep -qE "https://github\\.com/${TARGET_ORG}/" "$file"; then
        TARGET_FILES+=("$file")
    fi
done < <(find . -type f -name "*.md" -not -path "*/.*" -print0)

if [ ${#TARGET_FILES[@]} -eq 0 ]; then
    echo "[-] No absolute TCOS GitHub links detected inside local Markdown nodes."
    exit 0
fi

echo "================================================================================"
echo "                      TCOS LINK OPTIMIZATION AUDIT REPORT                       "
echo "================================================================================"
echo "Target Store Base: $STORE_FILE"
echo "Batch Boundary Max: $BATCH_LIMIT updates per runtime execution"
echo "--------------------------------------------------------------------------------"
echo "File Count Identified: ${#TARGET_FILES[@]}"
echo ""

total_estimated_changes=0
for file in "${TARGET_FILES[@]}"; do
    occurrences=$(grep -cE "https://github\\.com/${TARGET_ORG}/" "$file" || true)
    total_estimated_changes=$((total_estimated_changes + occurrences))
    echo "  -> File: $file ($occurrences absolute link instances)"
done
echo "--------------------------------------------------------------------------------"
echo "Total global changes indexed: $total_estimated_changes"
echo "================================================================================"
echo ""

read -p "Initialize interactive batch processing loop? (y/N): " init_choice
case "$init_choice" in 
    [yY][eE][sS]|[yY]) echo "[+] Beginning interactive execution context..." ;;
    *) echo "[-] Execution halted by operator command."; exit 0 ;;
esac

if [ ! -f "$STORE_FILE" ]; then
    touch "$STORE_FILE"
fi

processed_changes=0

for file in "${TARGET_FILES[@]}"; do
    line_num=0
    while IFS= read -r line; do
        line_num=$((line_num + 1))
        
        if [[ "$line" =~ https://github.com(${TARGET_ORG})/([^/\)]+) ]]; then
            if [ "$processed_changes" -ge "$BATCH_LIMIT" ]; then
                echo "================================================================================"
                echo "[!] Batch processing threshold ($BATCH_LIMIT) reached. Suspending thread."
                echo "================================================================================"
                exit 0
            fi

            matched_url=$(echo "$line" | grep -oE "https://github\\.com/${TARGET_ORG}/[^/\)]+" | head -n1)
            target_repo=$(echo "$matched_url" | awk -F'/' '{print $5}')
            proposed_relative="../$target_repo"

            change_hash=$(echo -n "${file}:${line_num}:${matched_url}" | md5sum | awk '{print $1}')

            if grep -q "$change_hash" "$STORE_FILE"; then
                continue
            fi

            echo ""
            echo "--------------------------------------------------------------------------------"
            echo "Match Index: $change_hash"
            echo "Target File: $file (Line $line_num)"
            echo "Current Raw: $line"
            echo "Proposed:    ${line//$matched_url/$proposed_relative}"
            echo "--------------------------------------------------------------------------------"
            
            read -p "Commit this mutation trace? (y/N): " record_choice
            case "$record_choice" in
                [yY][eE][sS]|[yY])
                    escaped_match=$(printf '%s\n' "$matched_url" | sed 's:[][\/.^$*]:\\&:g')
                    escaped_replace=$(printf '%s\n' "$proposed_relative" | sed 's:[][\/.^$*]:\\&:g')
                    sed -i "${line_num}s/${escaped_match}/${escaped_replace}/" "$file"
                    echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') | $change_hash | $file | $target_repo" >> "$STORE_FILE"
                    processed_changes=$((processed_changes + 1))
                    echo "[+] Mutation integrated and hashed."
                    ;;
                *)
                    echo "[*] Change deferred by user instruction."
                    ;;
            esac
        fi
    done < "$file"
done
chmod +x bin/relative-link-fixer.sh
