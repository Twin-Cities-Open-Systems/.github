# bulk_org_repo_readme_update.bash

for repo in $(./bin/manage-org-repos.sh --names-only); do
    target_readme="${HOME}/git/${repo}/README.md"
    if [ -d "${HOME}/git/${repo}" ]; then
        # Write custom repository title and classification header
        echo "# ${repo}" > "$target_readme"
        echo "" >> "$target_readme"
        
        # Append the global structural template specifications
        tail -n +3 profile/SUB_README_TEMPLATE.md >> "$target_readme"
        echo "[✅] Standardized documentation template injected into: $repo"
    fi
done

