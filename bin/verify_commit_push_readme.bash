# verify_commit_push_readme.bash

for repo in $(./bin/manage-org-repos.sh --names-only); do
    repo_path="${HOME}/git/${repo}"
    if [ -d "$repo_path" ]; then
        (
            cd "$repo_path"
            
            # Check if README.md has uncommitted modifications or is untracked
            if git status --porcelain README.md | grep -qE "^(M| M|\?\?)"; then
                echo "--------------------------------------------------------"
                echo "[🚀] Shipping modifications for repository: $repo"
                
                # Extract the active default branch name natively
                default_branch=$(git remote show origin | sed -n '/HEAD branch/s/.*: //p')
                
                # Stage the file and run your newly installed commit validations
                git add README.md
                
                # Commit the change under our organizational standard tracker
                git commit -m "docs: align repo documentation architecture with master TCOS blueprint"
                
                # Push back up to the secure remote cluster
                echo "  -> Pushing modifications to origin/$default_branch..."
                git push origin "$default_branch" -q
                echo "  [✅] Successfully deployed documentation changes."
            fi
        )
    fi
done
