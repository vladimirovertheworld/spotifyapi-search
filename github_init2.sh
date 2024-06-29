#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to handle errors
handle_error() {
    echo -e "${RED}Error: $1${NC}"
    exit 1
}

# Function to handle warnings
handle_warning() {
    echo -e "${YELLOW}Warning: $1${NC}"
}

# Function to prompt user for action
prompt_user() {
    read -p "$1 (y/n): " response
    case $response in
        [Yy]* ) return 0 ;;
        * ) return 1 ;;
    esac
}

# Function to check for SSH key
check_ssh_key() {
    if [ ! -f ~/.ssh/id_rsa.pub ]; then
        handle_warning "No SSH key found. Would you like to generate one?"
        if prompt_user "Generate SSH key?"; then
            ssh-keygen -t rsa -b 4096 -C "$(git config user.email)" || handle_error "Failed to generate SSH key"
            echo -e "${GREEN}SSH key generated successfully.${NC}"
            echo -e "${BLUE}Please add the following public key to your GitHub account:${NC}"
            cat ~/.ssh/id_rsa.pub
            echo -e "${YELLOW}After adding the key to GitHub, press any key to continue...${NC}"
            read -n 1 -s
        else
            echo "Proceeding without SSH key. You may need to use HTTPS for git operations."
        fi
    else
        echo -e "${GREEN}SSH key found.${NC}"
    fi
}

# Check if git is installed
if ! command_exists git; then
    handle_error "git is not installed. Please install git and try again."
fi

# Check for SSH key
check_ssh_key

# Check if current directory is already a git repository
if [ -d .git ]; then
    if prompt_user "This directory is already a git repository. Do you want to reinitialize it?"; then
        rm -rf .git || handle_error "Failed to remove existing .git directory"
    else
        echo "Exiting without changes."
        exit 0
    fi
fi

# Initialize git repository
git init || handle_error "Failed to initialize git repository"
echo -e "${GREEN}Git repository initialized successfully.${NC}"

# Ask for GitHub repository URL
while true; do
    read -p "Enter your GitHub repository URL (SSH or HTTPS): " repo_url
    if [[ $repo_url =~ ^(https://github.com/.+/.+\.git|git@github.com:.+/.+\.git)$ ]]; then
        break
    else
        handle_warning "Invalid GitHub repository URL. It should be in the format:"
        echo "HTTPS: https://github.com/username/repository.git"
        echo "SSH: git@github.com:username/repository.git"
    fi
done

# Add remote origin
git remote add origin $repo_url || handle_error "Failed to add remote origin"
echo -e "${GREEN}Remote origin added successfully.${NC}"

# Create initial commit
git add . || handle_warning "Failed to stage files"
git commit -m "Initial commit" || {
    handle_warning "Failed to create initial commit. Attempting to configure git user..."
    read -p "Enter your Git username: " git_username
    read -p "Enter your Git email: " git_email
    git config user.name "$git_username" || handle_error "Failed to set git username"
    git config user.email "$git_email" || handle_error "Failed to set git email"
    git commit -m "Initial commit" || handle_error "Failed to create initial commit after configuring user"
}
echo -e "${GREEN}Initial commit created successfully.${NC}"

# Push to remote repository
echo -e "${BLUE}Attempting to push to remote repository...${NC}"
if ! git push -u origin main; then
    handle_warning "Push to 'main' branch failed. Attempting to pull and resolve conflicts..."
    if git pull origin main --rebase; then
        handle_warning "Conflicts detected. Please resolve them manually."
        echo -e "${BLUE}Follow these steps to resolve conflicts:${NC}"
        echo "1. Open the conflicted files and resolve the conflicts manually."
        echo "2. Use 'git add <conflicted_files>' to mark them as resolved."
        echo "3. Continue the rebase with 'git rebase --continue'."
        echo "4. After resolving conflicts, push the changes with 'git push -u origin main'."
        exit 1
    else
        handle_error "Failed to pull remote changes"
    fi
else
    echo -e "${GREEN}Successfully pushed to 'main' branch.${NC}"
fi

# Final checks
if ! git remote -v | grep -q origin; then
    handle_warning "Remote 'origin' is not set. Please check your repository configuration."
fi

if [ -z "$(git log -1 --pretty=%B)" ]; then
    handle_warning "No commits found. Ensure you have committed your changes."
fi

echo -e "${BLUE}Deployment script execution completed.${NC}"
