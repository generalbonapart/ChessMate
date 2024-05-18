# Prompt the user for a commit message
$commitMessage = Read-Host "Enter your commit message"

# Navigate to your repository directory
# Ensure you update this path to your actual repository path
cd "E:\ChessMate"

# Add all changes to the staging area
git add .

# Commit the changes with the user's message
git commit -m "$commitMessage"

# Push the changes to the remote repository
git push

Write-Host "Changes have been pushed to the remote repository."