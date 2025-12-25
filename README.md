# Central Repository Setup - Reusable Workflows

## 🎯 Architecture Overview

```
github-actions-shared/                  ← Central repository (ONE TIME SETUP)
├── .github/workflows/
│   └── ai-code-review-reusable.yml    ← The reusable workflow
├── code_reviewer.py                    ← Your CLI tool
├── logger.py                           ← Logger module
├── requirements.txt
└── README.md

project-a/                              ← Any project (MINIMAL SETUP)
└── .github/workflows/
    └── ai-code-review.yml             ← 15 lines that call central workflow

project-b/                              ← Another project
└── .github/workflows/
    └── ai-code-review.yml             ← Same 15 lines

project-c/                              ← Yet another project
└── .github/workflows/
    └── ai-code-review.yml             ← Same 15 lines
```

## 📦 Step 1: Create Central Repository

### 1.1 Create the Repository
```bash
# Create a new repository for shared workflows
# Can be named: github-actions-shared, .github-workflows, or anything you like

# Option 1: Public repository (works everywhere, free GitHub plan)
# Option 2: Private repository (requires GitHub Enterprise for cross-repo use)
```

### 1.2 Add Your Files
```bash
cd github-actions-shared

# Add the reusable workflow
mkdir -p .github/workflows
# Copy the "Central Reusable Workflow" artifact content to:
# .github/workflows/ai-code-review-reusable.yml

# Add your Python files
# Copy code_reviewer.py
# Copy logger.py

# Add requirements
cat << EOF > requirements.txt
anthropic>=0.39.0
python-dotenv>=1.0.0
EOF

# Commit and push
git add .
git commit -m "feat: add reusable AI code review workflow"
git push origin main
```

### 1.3 Add Secret

#### 1.3.1 Organization

1. Go to **Organization Settings** → **Secrets and variables** → **Actions**
2. Click **New organization secret**
3. Name: `ANTHROPIC_API_KEY`
4. Value: Your API key
5. **Repository access**: Select "All repositories" or specific ones
6. Click **Add secret**

#### 1.3.2 Project (less efficient but works)

1. Go to **Project Settings** → **Secrets and variables** → **Actions**
2. Click **New secret**
3. Name: `ANTHROPIC_API_KEY`
4. Value: Your API key
5. Click **Add secret**

## 🚀 Step 2: Use in Any Project (2 Minutes Per Project!)

### 2.1 Create Caller Workflow
In **each project** you want to use the AI reviewer:

```bash
cd your-project

# Create workflow directory
mkdir -p .github/workflows

# Create the caller workflow
cat << 'EOF' > .github/workflows/ai-code-review.yml
name: AI Code Review

on:
  issue_comment:
    types: [created]

jobs:
  trigger-review:
    if: |
      github.event.issue.pull_request &&
      contains(github.event.comment.body, '@haiku review')
    
    uses: YOUR-ORG/github-actions-shared/.github/workflows/ai-code-review-reusable.yml@main
    secrets: inherit
EOF

# Replace YOUR-ORG with your GitHub organization/username
sed -i 's/YOUR-ORG/your-github-org/g' .github/workflows/ai-code-review.yml

# Commit and push
git add .github/workflows/ai-code-review.yml
git commit -m "feat: add AI code review"
git push origin main
```

### 2.2 That's It!
No need to:
- ❌ Copy `code_reviewer.py`
- ❌ Copy `logger.py`
- ❌ Add dependencies
- ❌ Manage API keys per project

Just the **15-line YAML file** and you're done! 🎉

## 🔄 Updates - The Magic Part

When you improve the review logic:

```bash
cd github-actions-shared

# Edit code_reviewer.py to improve prompts
vim code_reviewer.py

# Commit and push
git commit -am "feat: improve code review prompts"
git push origin main
```

**ALL projects automatically use the new version!** 🚀

No need to update 50 different repositories!

## 🏷️ Best Practices: Versioning

For production stability, use tags:

```bash
# In central repo
cd github-actions-shared

# Create a version tag
git tag -a v1.0.0 -m "Stable release v1.0.0"
git push origin v1.0.0

# Later, create v1.1.0, v2.0.0, etc.
```

Then in projects, reference specific versions:
```yaml
uses: YOUR-ORG/github-actions-shared/.github/workflows/ai-code-review-reusable.yml@v1.0.0
```

**Versioning strategy:**
- `@main` - Always latest (for development projects)
- `@v1` - Major version (gets minor updates automatically)
- `@v1.0.0` - Exact version (maximum stability)

## 🔐 Security Notes

### For Private Repositories
If your central repo is private:
1. Need GitHub Enterprise plan
2. Or all repos must be in the same repository
3. Or make the central repo public (no sensitive data anyway)

### For Public Repositories
- Works on all GitHub plans (Free, Pro, Team, Enterprise)
- Anyone can use the workflow if they find it

## 💡 Advanced: Multiple Workflows

You can have multiple reusable workflows in the central repo:

```
github-actions-shared/
├── .github/workflows/
│   ├── ai-code-review-reusable.yml      ← Code review
│   ├── auto-merge-reusable.yml          ← Auto-merge PRs
│   ├── security-scan-reusable.yml       ← Security scanning
│   └── deploy-to-staging-reusable.yml   ← Deployment
```

Each project picks which ones to use!

## Troubleshooting

### "Workflow not found"
```bash
# Check the path is correct:
# YOUR-ORG/REPO-NAME/.github/workflows/FILE-NAME.yml@BRANCH

# Verify the central repo is accessible
# For private repos: check organization settings
```

### "Secret not found"
```bash
# If using organization secrets:
# 1. Check organization settings → Secrets
# 2. Verify repository access is granted

# If using repository secrets:
# Add ANTHROPIC_API_KEY to EACH project repository
```

### "Permission denied"
```bash
# For private repos in different organizations: won't work
# Solution: Make central repo public OR use GitHub Enterprise
```


## Examples

![AI reactions](https://github.com/Rashaann/github-actions-shared/blob/main/images/bot_reaction.png?raw=true)

![AI review](https://github.com/Rashaann/github-actions-shared/blob/main/images/bot_review.png?raw=true)
