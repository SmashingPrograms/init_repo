# Repository Initializer

Automate the creation of GitHub repositories with local git setup.

## Features

- Creates GitHub repositories via API
- Sets up local git repository with initial commit
- Configurable via JSON file
- Comprehensive test suite
- Detailed logging and error handling
- Can be installed globally for system-wide access

## Prerequisites

- Python 3.6+
- Git installed and configured
- GitHub account with SSH access set up
- GitHub Personal Access Token

## Installation & Setup

### 1. Install Dependencies

```bash
pip3 install requests
```

### 2. Download the Script

```bash
curl -O https://raw.githubusercontent.com/your-repo/init_repo.py
chmod +x init_repo.py
```

### 3. Create Configuration File

Create a `config.json` file in the same directory as the script:

```json
{
  "github_token": "your_github_personal_access_token_here",
  "github_username": "YourGitHubUsername",
  "ssh_alias": "your-ssh-alias",
  "default_branch": "main"
}
```

**Configuration Details:**

- **github_token**: Your GitHub Personal Access Token with `repo` scope
  - Go to GitHub Settings → Developer settings → Personal access tokens
  - Create a new token with `repo` permissions
- **github_username**: Your GitHub username
- **ssh_alias**: Your SSH alias for GitHub (from `~/.ssh/config`)
- **default_branch**: Default branch name (usually `main`)

### 4. Set Up GitHub Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Click "Generate new token"
3. Select scopes: `repo` (full control of private repositories)
4. Copy the token and add it to your `config.json`

### 5. Set Up SSH Configuration

Edit `~/.ssh/config` to include your GitHub SSH configuration:

```
Host github-smashing
    HostName github.com
    User git
    IdentityFile ~/.ssh/your_private_key
    IdentitiesOnly yes
```

Replace `github-smashing` with your preferred alias and update the `ssh_alias` in `config.json` accordingly.

### 6. Test the Setup

```bash
python3 init_repo.py --test
```

This will run a comprehensive test suite to verify:
- Configuration loading
- GitHub API connectivity
- Git availability
- SSH configuration

## Global Installation (Run from Anywhere)

To use `init_repo` command from anywhere on your system:

### Method 1: Using Homebrew (Recommended for macOS)

```bash
# Create a formula directory
mkdir -p /usr/local/Homebrew/Library/Taps/homebrew/homebrew-local/Formula

# Create the formula
cat > /usr/local/Homebrew/Library/Taps/homebrew/homebrew-local/Formula/init-repo.rb << 'EOF'
class InitRepo < Formula
  desc "GitHub repository initializer"
  homepage "https://github.com/your-repo"
  url "file:///path/to/your/init_repo.py"
  version "1.0.0"

  def install
    bin.install "init_repo.py" => "init_repo"
  end

  test do
    system "#{bin}/init_repo", "--help"
  end
end
EOF

# Install
brew install init-repo
```

### Method 2: Manual Symlink Method

```bash
# Make the script executable
chmod +x init_repo.py

# Create a symlink in your PATH
sudo ln -sf "$(pwd)/init_repo.py" /usr/local/bin/init_repo

# OR copy to a directory in your PATH
sudo cp init_repo.py /usr/local/bin/init_repo
```

### Method 3: Add to PATH via ~/.zshrc (or ~/.bash_profile)

```bash
# Add this directory to your PATH
echo 'export PATH="$PATH:$(pwd)"' >> ~/.zshrc

# Reload your shell
source ~/.zshrc

# Create an alias
echo 'alias init_repo="python3 $(dirname $(which init_repo.py))/init_repo.py"' >> ~/.zshrc
```

### Method 4: Create a Shell Script Wrapper

```bash
# Create a wrapper script
cat > /usr/local/bin/init_repo << 'EOF'
#!/bin/bash
python3 /path/to/your/init_repo.py "$@"
EOF

# Make it executable
chmod +x /usr/local/bin/init_repo
```

## Usage

### Create a New Repository

```bash
# If installed globally
init_repo my_awesome_project

# If running locally
python3 init_repo.py my_awesome_project
```

### Run Tests

```bash
init_repo --test
# or
python3 init_repo.py --test
```

### Verbose Mode

```bash
init_repo my_project --verbose
```

### Custom Config File

```bash
init_repo my_project --config /path/to/custom/config.json
```

## What It Does

When you run `init_repo project_name`, it will:

1. **Create GitHub Repository**: Uses GitHub API to create a new repository
2. **Create Local Directory**: `mkdir project_name`
3. **Initialize Git**: `git init` in the new directory
4. **Create README.md**: With project name as header
5. **Create .gitignore**: With common patterns for macOS, Node.js, Python, etc.
6. **Initial Commit**: Adds all files and makes first commit
7. **Set Default Branch**: Sets to `main` (or configured branch)
8. **Add Remote**: Adds GitHub repository as origin
9. **Push**: Pushes the initial commit to GitHub

## File Structure

After successful execution:

```
project_name/
├── README.md
├── .gitignore
└── .git/
    └── (git repository files)
```

## Troubleshooting

### Common Issues

**"Repository already exists"**: The script will continue with local setup if the GitHub repo already exists.

**SSH Permission Denied**: 
- Verify your SSH key is added to GitHub
- Check your SSH config file
- Test with: `ssh -T git@your-ssh-alias`

**GitHub API 401 Unauthorized**:
- Verify your GitHub token is correct
- Ensure token has `repo` scope
- Check token hasn't expired

**Git command not found**:
- Install Git: `brew install git`
- Ensure Git is in your PATH

### Log Files

The script creates detailed logs in `init_repo.log` for debugging issues.

### Verify Setup

```bash
# Test GitHub API connection
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user

# Test SSH connection
ssh -T git@your-ssh-alias

# Test Git
git --version
```

## Configuration Options

| Option | Description | Example |
|--------|-------------|---------|
| `github_token` | GitHub Personal Access Token | `ghp_xxxxxxxxxxxx` |
| `github_username` | Your GitHub username | `SmashingPrograms` |
| `ssh_alias` | SSH alias from ~/.ssh/config | `github-smashing` |
| `default_branch` | Default branch name | `main` |

## Security Notes

- Keep your `config.json` file secure and never commit it to version control
- Consider using environment variables for the GitHub token in production
- The GitHub token should have minimal required permissions (`repo` scope only)

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source. Use it however you'd like!