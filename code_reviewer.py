#!/usr/bin/env python3
"""
AI-Powered Code Reviewer CLI
Uses Claude Haiku 4.5 to review git diffs and provide actionable feedback
"""

import anthropic
import argparse
from dotenv import load_dotenv
from logger import logger
from pathlib import Path
import os
import subprocess
import sys

load_dotenv()

class CodeReviewer:
    def __init__(self, api_key=None):
        """Initialize the code reviewer with Anthropic API key"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. Set it as an environment variable or pass it directly."
            )
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-haiku-4-5"  # Claude Haiku 4.5
    
    def get_git_diff(self, target_branch="main", staged_only=False):
        """Get git diff from current branch"""
        try:
            if staged_only:
                # Get only staged changes
                cmd = ["git", "diff", "--cached"]
            else:
                # Get diff against target branch
                cmd = ["git", "diff", f"{target_branch}...HEAD"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting git diff: {e.stderr}")
            return None
    
    def review_code(self, diff_content, context=""):
        """Send diff to Claude for review"""
        
        system_prompt = """You are an expert code reviewer. Analyze the provided git diff and provide a thorough, actionable code review.

Focus on:
1. **Bugs & Logic Errors**: Potential runtime errors, edge cases, null/undefined handling
2. **Security Issues**: Vulnerabilities, injection risks, authentication/authorization problems
3. **Performance**: Inefficient algorithms, memory leaks, unnecessary computations
4. **Code Quality**: Readability, maintainability, naming conventions, complexity
5. **Best Practices**: Language-specific idioms, design patterns, error handling

Format your review as:
## Summary
Brief overview of changes and overall assessment

## Critical Issues (🔴)
Issues that must be fixed before merge

## Warnings (🟡)
Important issues to address

## Suggestions (🟢)
Nice-to-have improvements

## Positive Notes (✅)
What was done well

Be specific, reference line numbers when possible, and provide code examples for fixes."""

        user_prompt = f"""Review this code change:

{context}

```diff
{diff_content}
```

Provide a detailed review following the format specified."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                system=system_prompt
            )
            
            return message.content[0].text
        
        except anthropic.APIError as e:
            logger.error(f"Anthropic API Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during API call: {type(e).__name__}: {e}")
            return None
    
    def format_review(self, review_text):
        """Format and colorize the review output"""
        # Simple terminal colors
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        
        # Add some visual separation
        print("\n" + "="*80)
        print(f"{BOLD}{HEADER}🤖 AI CODE REVIEW{ENDC}")
        print("="*80 + "\n")
        
        # Log the review with basic formatting
        lines = review_text.split('\n')
        for line in lines:
            if line.startswith('## Critical'):
                print(f"{FAIL}{BOLD}{line}{ENDC}")
            elif line.startswith('## Warning'):
                print(f"{WARNING}{BOLD}{line}{ENDC}")
            elif line.startswith('## Suggestion'):
                print(f"{OKBLUE}{BOLD}{line}{ENDC}")
            elif line.startswith('## Positive'):
                print(f"{OKGREEN}{BOLD}{line}{ENDC}")
            elif line.startswith('##'):
                print(f"{BOLD}{line}{ENDC}")
            else:
                print(line)
        
        print("\n" + "="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='AI-powered code reviewer using Claude Haiku 4.5'
    )
    parser.add_argument(
        '--diff-file',
        type=str,
        help='Path to a diff file (if not provided, will get from git)'
    )
    parser.add_argument(
        '--target-branch',
        type=str,
        default='main',
        help='Target branch to compare against (default: main)'
    )
    parser.add_argument(
        '--staged',
        action='store_true',
        help='Review only staged changes'
    )
    parser.add_argument(
        '--context',
        type=str,
        default='',
        help='Additional context about the changes'
    )
    
    args = parser.parse_args()
    
    # Initialize reviewer
    try:
        reviewer = CodeReviewer()
    except ValueError as e:
        logger.error(f"Error: {e}")
        logger.error("\nTo set up your API key:")
        logger.error("  export ANTHROPIC_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Get the diff
    if args.diff_file:
        # Read from file
        try:
            with open(args.diff_file, 'r') as f:
                diff_content = f.read()
        except FileNotFoundError:
            logger.error(f"Error: File '{args.diff_file}' not found")
            sys.exit(1)
    else:
        # Get from git
        logger.info("📊 Getting git diff...")
        diff_content = reviewer.get_git_diff(
            target_branch=args.target_branch,
            staged_only=args.staged
        )
        
        if not diff_content:
            logger.info("No changes found to review.")
            sys.exit(1)
        
        if not diff_content.strip():
            logger.info("No changes found to review.")
            sys.exit(0)
    
    # Review the code
    logger.info("🤖 Reviewing code with Claude Haiku 4.5...\n")
    review = reviewer.review_code(diff_content, context=args.context)
    
    if review:
        reviewer.format_review(review)
    else:
        logger.error("Failed to get review from API. Check the error messages above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
