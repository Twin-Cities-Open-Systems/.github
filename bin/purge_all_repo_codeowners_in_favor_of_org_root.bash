# bin/purge_all_repo_codeowners_in_favor_of_org_root.bash

for repo in $(~/git/.github/bin/manage-org-repos.sh --names-only); do
    # Skip processing your primary command center config directory entirely
    if [ "$repo" = ".github" ]; then
        continue
    fi
    
    repo_path="${HOME}/git/${repo}"
    if [ -d "$repo_path" ]; then
        echo "🧹 Auditing local code ownership footprint inside: $repo"
        
        # Systematically eliminate scattered local files
        rm -f "${repo_path}/CODEOWNERS" \
              "${repo_path}/.github/CODEOWNERS" \
              "${repo_path}/docs/CODEOWNERS"
    fi
done

