#!/bin/bash

# gitpush.sh - Script to add, commit, and push changes to GitHub

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install Git and try again."
    exit 1
fi

# Check if the script is run in a Git repository
if [ ! -d ".git" ]; then
    echo "This is not a Git repository. Please run this script in a valid Git repository."
    exit 1
fi

# Check for user authorization
if ! git config user.name &> /dev/null || ! git config user.email &> /dev/null; then
    echo "Git user is not configured. Please set up your Git user credentials."
    echo "Run the following commands to configure Git:"
    echo "  git config --global user.name \"Your Name\""
    echo "  git config --global user.email \"youremail@example.com\""
    exit 1
fi

# Add all changes to the staging area
git add .
if [ $? -ne 0 ]; then
    echo "Failed to add changes to the staging area."
    exit 1
fi

# Commit the changes
read -p "Enter commit message: " commit_message
git commit -m "$commit_message"
if [ $? -ne 0 ]; then
    echo "Failed to commit changes. Make sure you have staged changes to commit."
    exit 1
fi

# Push the changes to the remote repository
branch_name=$(git branch --show-current)
if [ -z "$branch_name" ]; then
    echo "Failed to detect the current branch."
    exit 1
fi

git push origin "$branch_name"
if [ $? -ne 0 ]; then
    echo "Failed to push changes to the remote repository."
    exit 1
fi

echo "Changes have been successfully pushed to GitHub."

exit 0
