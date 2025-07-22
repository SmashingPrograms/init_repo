#!/usr/bin/env python3
"""
GitHub Repository Initialization Script

This script automates the process of creating a new GitHub repository and 
setting up a local git repository with initial commit.

Usage:
    python3 init_repo.py <project_name>
    python3 init_repo.py --test
    python3 init_repo.py --help

Author: Your Name
Date: 2025
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests


class RepoInitializer:
    """Handles GitHub repository creation and local git setup."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the RepoInitializer.
        
        Args:
            config_path (str): Path to configuration file
        """
        self.config_path = config_path
        self._setup_logging()  # Set up logging FIRST
        self.config = self._load_config()
        
    def _setup_logging(self) -> None:
        """Configure logging for the application."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('init_repo.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self) -> Dict:
        """
        Load configuration from JSON file.
        
        Returns:
            Dict: Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        # Try to find config file in multiple locations
        possible_paths = [
            self.config_path,  # Provided path or default "config.json"
            os.path.join(os.path.dirname(__file__), self.config_path),  # Same dir as script
            os.path.join(os.path.expanduser("~"), ".config", "init_repo", self.config_path),  # User config dir
            os.path.join(os.path.expanduser("~"), self.config_path)  # Home directory
        ]
        
        config_file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                config_file_path = path
                self.logger.info(f"Found config file at: {path}")
                break
                
        if not config_file_path:
            self.logger.error(f"Config file not found. Searched in:")
            for path in possible_paths:
                self.logger.error(f"  - {path}")
            self._create_sample_config()
            raise FileNotFoundError(f"Config file '{self.config_path}' not found")
        
        try:
            with open(config_file_path, 'r') as f:
                config = json.load(f)
                
            # Validate required configuration keys
            required_keys = ['github_token', 'github_username', 'ssh_alias']
            missing_keys = [key for key in required_keys if key not in config]
            
            if missing_keys:
                raise ValueError(f"Missing required config keys: {missing_keys}")
                
            return config
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {e}")
            raise
            
    def _create_sample_config(self) -> None:
        """Create a sample configuration file."""
        # Create config in the same directory as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "config.json")
        
        sample_config = {
            "github_token": "your_github_personal_access_token_here",
            "github_username": "YourGitHubUsername",
            "ssh_alias": "github-alias",
            "default_branch": "main"
        }
        
        try:
            with open(config_path, 'w') as f:
                json.dump(sample_config, f, indent=2)
                
            self.logger.info(f"Created sample config file: {config_path}")
            self.logger.info("Please edit the config file with your actual values")
        except Exception as e:
            self.logger.error(f"Failed to create sample config: {e}")
            print(f"Please create a config.json file manually with your settings")
        
    def _run_command(self, command: str, cwd: Optional[str] = None, 
                    check: bool = True) -> Tuple[bool, str, str]:
        """
        Execute a shell command.
        
        Args:
            command (str): Command to execute
            cwd (Optional[str]): Working directory
            check (bool): Whether to raise exception on non-zero exit
            
        Returns:
            Tuple[bool, str, str]: (success, stdout, stderr)
        """
        self.logger.debug(f"Running command: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=check
            )
            
            self.logger.debug(f"Command output: {result.stdout}")
            if result.stderr:
                self.logger.debug(f"Command stderr: {result.stderr}")
                
            return True, result.stdout.strip(), result.stderr.strip()
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {command}")
            self.logger.error(f"Exit code: {e.returncode}")
            self.logger.error(f"Stdout: {e.stdout}")
            self.logger.error(f"Stderr: {e.stderr}")
            return False, e.stdout.strip() if e.stdout else "", e.stderr.strip() if e.stderr else ""
            
    def create_github_repo(self, repo_name: str) -> bool:
        """
        Create a new repository on GitHub.
        
        Args:
            repo_name (str): Name of the repository to create
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info(f"Creating GitHub repository: {repo_name}")
        
        url = "https://api.github.com/user/repos"
        headers = {
            "Authorization": f"token {self.config['github_token']}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        data = {
            "name": repo_name,
            "description": f"Repository for {repo_name}",
            "private": False,  # Set to True if you want private repos by default
            "auto_init": False
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 201:
                self.logger.info(f"Successfully created GitHub repository: {repo_name}")
                return True
            elif response.status_code == 422:
                error_msg = response.json().get('message', 'Unknown error')
                if 'already exists' in error_msg.lower():
                    self.logger.warning(f"Repository {repo_name} already exists on GitHub")
                    return True  # Consider this a success for our purposes
                else:
                    self.logger.error(f"GitHub API error: {error_msg}")
                    return False
            else:
                self.logger.error(f"Failed to create repository. Status: {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return False
                
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return False
            
    def setup_local_repo(self, repo_name: str) -> bool:
        """
        Set up local git repository with initial commit.
        
        Args:
            repo_name (str): Name of the repository
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info(f"Setting up local repository: {repo_name}")
        
        # Check if directory already exists
        if os.path.exists(repo_name):
            self.logger.error(f"Directory {repo_name} already exists")
            return False
            
        # Create directory and navigate to it
        success, _, _ = self._run_command(f"mkdir {repo_name}")
        if not success:
            return False
            
        # Create README.md
        readme_content = f"# {repo_name}\n"
        readme_path = os.path.join(repo_name, "README.md")
        
        try:
            with open(readme_path, 'w') as f:
                f.write(readme_content)
        except IOError as e:
            self.logger.error(f"Failed to create README.md: {e}")
            return False
            
        # Initialize git repository
        success, _, _ = self._run_command("git init", cwd=repo_name)
        if not success:
            return False
            
        # Create .gitignore file
        if not self._create_gitignore(repo_name):
            return False
            
        # Add files and make initial commit
        success, _, _ = self._run_command("git add .", cwd=repo_name)
        if not success:
            return False
            
        success, _, _ = self._run_command('git commit -m "first commit"', cwd=repo_name)
        if not success:
            return False
            
        # Set default branch
        default_branch = self.config.get('default_branch', 'main')
        success, _, _ = self._run_command(f"git branch -M {default_branch}", cwd=repo_name)
        if not success:
            return False
            
        # Add remote origin
        remote_url = f"git@{self.config['ssh_alias']}:{self.config['github_username']}/{repo_name}.git"
        success, _, _ = self._run_command(f"git remote add origin {remote_url}", cwd=repo_name)
        if not success:
            return False
            
        # Push to remote
        success, _, _ = self._run_command(f"git push -u origin {default_branch}", cwd=repo_name)
        if not success:
            self.logger.error("Failed to push to remote. Check your SSH configuration.")
            return False
            
        self.logger.info(f"Successfully set up local repository: {repo_name}")
        return True
        
    def _create_gitignore(self, repo_name: str) -> bool:
        """
        Create .gitignore file with common patterns.
        
        Args:
            repo_name (str): Name of the repository
            
        Returns:
            bool: True if successful, False otherwise
        """
        gitignore_content = """# macOS
.DS_Store
.AppleDouble
.LSOverride

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
env/
venv/
ENV/

# VSCode
.vscode/

# JetBrains IDEs
.idea/
*.iml

# Logs
logs/
*.log

# Environment files
.env
.env.*

# Build output
dist/
build/

# Misc
*.swp
*~ 
"""
        
        gitignore_path = os.path.join(repo_name, ".gitignore")
        
        try:
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)
            self.logger.debug("Created .gitignore file")
            return True
        except IOError as e:
            self.logger.error(f"Failed to create .gitignore: {e}")
            return False
            
    def initialize_repo(self, repo_name: str) -> bool:
        """
        Complete repository initialization process.
        
        Args:
            repo_name (str): Name of the repository
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info(f"Starting repository initialization: {repo_name}")
        
        # Create GitHub repository
        if not self.create_github_repo(repo_name):
            return False
            
        # Set up local repository
        if not self.setup_local_repo(repo_name):
            return False
            
        self.logger.info(f"Repository {repo_name} initialized successfully!")
        return True


class TestSuite:
    """Test suite for the RepoInitializer."""
    
    def __init__(self, initializer: RepoInitializer):
        """
        Initialize the test suite.
        
        Args:
            initializer (RepoInitializer): RepoInitializer instance to test
        """
        self.initializer = initializer
        self.logger = logging.getLogger(__name__ + ".TestSuite")
        
    def test_config_loading(self) -> bool:
        """Test configuration loading."""
        self.logger.info("Testing configuration loading...")
        
        try:
            # Test if config is loaded properly
            required_keys = ['github_token', 'github_username', 'ssh_alias']
            missing_keys = [key for key in required_keys if key not in self.initializer.config]
            
            if missing_keys:
                self.logger.error(f"Missing config keys: {missing_keys}")
                return False
                
            # Test if values are not default/placeholder values
            if self.initializer.config['github_token'] == 'your_github_personal_access_token_here':
                self.logger.error("GitHub token appears to be placeholder value")
                return False
                
            self.logger.info("✓ Configuration loading test passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration loading test failed: {e}")
            return False
            
    def test_github_api_connection(self) -> bool:
        """Test GitHub API connection."""
        self.logger.info("Testing GitHub API connection...")
        
        try:
            url = "https://api.github.com/user"
            headers = {
                "Authorization": f"token {self.initializer.config['github_token']}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                username = user_data.get('login')
                self.logger.info(f"✓ GitHub API connection test passed (User: {username})")
                
                # Verify username matches config
                if username != self.initializer.config['github_username']:
                    self.logger.warning(f"Username mismatch: API says '{username}', config says '{self.initializer.config['github_username']}'")
                    
                return True
            else:
                self.logger.error(f"GitHub API connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"GitHub API connection test failed: {e}")
            return False
            
    def test_git_availability(self) -> bool:
        """Test if git is available in the system."""
        self.logger.info("Testing git availability...")
        
        success, stdout, stderr = self.initializer._run_command("git --version", check=False)
        
        if success and "git version" in stdout.lower():
            self.logger.info(f"✓ Git availability test passed ({stdout})")
            return True
        else:
            self.logger.error("Git is not available or not working properly")
            return False
            
    def test_ssh_configuration(self) -> bool:
        """Test SSH configuration for GitHub."""
        self.logger.info("Testing SSH configuration...")
        
        ssh_alias = self.initializer.config['ssh_alias']
        
        # Test SSH connection (this will likely fail but we can check the error type)
        success, stdout, stderr = self.initializer._run_command(
            f"ssh -T git@{ssh_alias}", 
            check=False
        )
        
        # GitHub SSH test returns exit code 1 even on success
        if "successfully authenticated" in stderr.lower() or "successfully authenticated" in stdout.lower():
            self.logger.info("✓ SSH configuration test passed")
            return True
        elif "permission denied" in stderr.lower():
            self.logger.error("SSH permission denied - check your SSH key configuration")
            return False
        elif "could not resolve hostname" in stderr.lower():
            self.logger.error(f"SSH alias '{ssh_alias}' could not be resolved - check your SSH config")
            return False
        else:
            # SSH might be working but we can't be sure - this is a soft pass
            self.logger.warning("SSH test inconclusive - check manually if needed")
            self.logger.debug(f"SSH test output: {stderr}")
            return True
            
    def run_all_tests(self) -> bool:
        """
        Run all tests.
        
        Returns:
            bool: True if all tests pass, False otherwise
        """
        self.logger.info("Running test suite...")
        
        tests = [
            self.test_config_loading,
            self.test_github_api_connection,
            self.test_git_availability,
            self.test_ssh_configuration
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                self.logger.error(f"Test {test.__name__} failed with exception: {e}")
                results.append(False)
                
        passed = sum(results)
        total = len(results)
        
        self.logger.info(f"Test results: {passed}/{total} tests passed")
        
        if passed == total:
            self.logger.info("✓ All tests passed!")
            return True
        else:
            self.logger.error(f"✗ {total - passed} tests failed")
            return False


def main():
    """Main function to handle command line arguments and execution."""
    parser = argparse.ArgumentParser(
        description="Initialize a new GitHub repository with local git setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 init_repo.py my_new_project     # Create repository 'my_new_project'
  python3 init_repo.py --test             # Run test suite
  python3 init_repo.py --help             # Show this help message
        """
    )
    
    parser.add_argument(
        'repo_name',
        nargs='?',
        help='Name of the repository to create'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run the test suite'
    )
    
    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    try:
        # Initialize the repo initializer
        initializer = RepoInitializer(config_path=args.config)
        
        if args.test:
            # Run test suite
            test_suite = TestSuite(initializer)
            success = test_suite.run_all_tests()
            sys.exit(0 if success else 1)
            
        elif args.repo_name:
            # Create repository
            success = initializer.initialize_repo(args.repo_name)
            
            if success:
                print(f"✓ Repository '{args.repo_name}' created successfully!")
                print(f"  - GitHub: https://github.com/{initializer.config['github_username']}/{args.repo_name}")
                print(f"  - Local: ./{args.repo_name}")
            else:
                print(f"✗ Failed to create repository '{args.repo_name}'")
                print("Check the log file 'init_repo.log' for details")
                
            sys.exit(0 if success else 1)
            
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n✗ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"✗ An error occurred: {e}")
        logging.getLogger().error(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()