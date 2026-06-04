#!/usr/bin/env bash
# Code Analyzer Suite — Cross-Platform Installer
# Supports: Claude Code, GitHub Copilot, Cursor, Windsurf, Trae, and more

set -euo pipefail

SKILL_NAME="code-analyzer-suite"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info() { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }

# Detect platform and install path
detect_platform() {
    local platform=""
    local install_path=""

    # Check for explicit platform argument
    if [[ "${1:-}" == "--platform" && -n "${2:-}" ]]; then
        platform="$2"
    fi

    # Auto-detect if not specified
    if [[ -z "$platform" ]]; then
        if [[ -d "$HOME/.claude" ]]; then
            platform="claude"
        elif [[ -d "$HOME/.copilot" ]]; then
            platform="copilot"
        elif [[ -d ".cursor" ]] || [[ -d "$HOME/.cursor" ]]; then
            platform="cursor"
        elif [[ -d "$HOME/.codeium/windsurf" ]] || [[ -d ".windsurf" ]]; then
            platform="windsurf"
        elif [[ -d ".trae" ]] || [[ -d "$HOME/.trae" ]]; then
            platform="trae"
        elif [[ -d "$HOME/.cline" ]] || [[ -d ".clinerules" ]]; then
            platform="cline"
        elif [[ -d "$HOME/.roo" ]] || [[ -d ".roo" ]]; then
            platform="roo"
        elif [[ -d "$HOME/.config/goose" ]]; then
            platform="goose"
        elif [[ -d "$HOME/.config/opencode" ]]; then
            platform="opencode"
        elif [[ -d "$HOME/.gemini" ]]; then
            platform="gemini"
        elif [[ -d "$HOME/.kiro" ]] || [[ -d ".kiro" ]]; then
            platform="kiro"
        elif [[ -d "$HOME/.agents" ]]; then
            platform="universal"
        else
            platform="universal"
        fi
    fi

    echo "$platform"
}

# Get install path for platform
get_install_path() {
    local platform="$1"
    local project_level="${2:-false}"

    case "$platform" in
        claude)
            echo "$HOME/.claude/skills/$SKILL_NAME"
            ;;
        copilot)
            if [[ "$project_level" == "true" ]]; then
                echo ".github/skills/$SKILL_NAME"
            else
                echo "$HOME/.copilot/skills/$SKILL_NAME"
            fi
            ;;
        cursor)
            echo ".cursor/skills/$SKILL_NAME"
            ;;
        windsurf)
            if [[ -d "$HOME/.codeium/windsurf" ]]; then
                echo "$HOME/.codeium/windsurf/skills/$SKILL_NAME"
            else
                echo ".windsurf/rules/$SKILL_NAME"
            fi
            ;;
        trae)
            echo ".trae/rules/$SKILL_NAME"
            ;;
        cline)
            if [[ -d "$HOME/.cline" ]]; then
                echo "$HOME/.cline/skills/$SKILL_NAME"
            else
                echo ".clinerules/skills/$SKILL_NAME"
            fi
            ;;
        roo|roo-code)
            if [[ -d "$HOME/.roo" ]]; then
                echo "$HOME/.roo/skills/$SKILL_NAME"
            else
                echo ".roo/skills/$SKILL_NAME"
            fi
            ;;
        goose)
            echo "$HOME/.config/goose/skills/$SKILL_NAME"
            ;;
        opencode)
            if [[ -d "$HOME/.config/opencode" ]]; then
                echo "$HOME/.config/opencode/skills/$SKILL_NAME"
            else
                echo ".opencode/skills/$SKILL_NAME"
            fi
            ;;
        gemini)
            echo "$HOME/.gemini/skills/$SKILL_NAME"
            ;;
        kiro)
            if [[ -d "$HOME/.kiro" ]]; then
                echo "$HOME/.kiro/skills/$SKILL_NAME"
            else
                echo ".kiro/skills/$SKILL_NAME"
            fi
            ;;
        universal|codex)
            echo "$HOME/.agents/skills/$SKILL_NAME"
            ;;
        *)
            echo "$HOME/.agents/skills/$SKILL_NAME"
            ;;
    esac
}

# Install skill to path
install_skill() {
    local target_path="$1"
    local platform="$2"

    info "Installing to: $target_path"

    # Create parent directory
    mkdir -p "$(dirname "$target_path")"

    # Remove existing installation
    if [[ -d "$target_path" ]]; then
        warn "Removing existing installation..."
        rm -rf "$target_path"
    fi

    # Copy skill files
    cp -R "$SKILL_DIR" "$target_path"

    success "Installed to: $target_path"
}

# Create symlink in universal path
create_universal_symlink() {
    local target_path="$1"
    local universal_path="$HOME/.agents/skills/$SKILL_NAME"

    if [[ "$target_path" != "$universal_path" ]]; then
        mkdir -p "$HOME/.agents/skills"
        if [[ -L "$universal_path" ]]; then
            rm "$universal_path"
        fi
        ln -s "$target_path" "$universal_path" 2>/dev/null || true
        success "Created universal symlink: $universal_path"
    fi
}

# Generate platform-specific format adaptations
adapt_format() {
    local target_path="$1"
    local platform="$2"

    case "$platform" in
        cursor)
            # Generate .mdc file for Cursor
            local mdc_file="$target_path/.cursor-rules.mdc"
            cat > "$mdc_file" << 'EOF'
---
description: Code Analyzer Suite — Parallel multi-dimensional code analysis
globs: ["**/*"]
alwaysApply: true
---

# /code-analyzer — Parallel Multi-Dimensional Code Analysis

You are an expert code analysis orchestrator. Your job is to decompose code review and analysis tasks into parallel subtasks across five specialized dimensions, then generate structured analysis reports.

## Analysis Dimensions
1. Security Analysis — vulnerabilities, injection risks, auth issues
2. Performance Analysis — bottlenecks, memory leaks, inefficient algorithms
3. Code Quality — style consistency, complexity, documentation
4. Architecture Review — design patterns, coupling, cohesion
5. Logic Verification — business logic correctness, edge cases

## Severity Ratings
Critical, High, Medium, Low

## Usage
User invokes `/code-analyzer` followed by their code review request.
EOF
            success "Generated Cursor .mdc format"
            ;;
        windsurf)
            # Windsurf uses plain .md with 6000 char limit
            local rule_file="$target_path/windsurf-rule.md"
            head -c 5900 "$target_path/SKILL.md" > "$rule_file"
            success "Generated Windsurf rule format"
            ;;
        trae)
            # Trae uses plain .md with type frontmatter
            local trae_file="$target_path/trae-rule.md"
            cat > "$trae_file" << 'EOF'
---
type: Always
---

# /code-analyzer — Parallel Multi-Dimensional Code Analysis

You are an expert code analysis orchestrator...
EOF
            success "Generated Trae rule format"
            ;;
    esac
}

# Print activation instructions
print_activation() {
    local platform="$1"

    echo ""
    echo "========================================"
    echo "  Code Analyzer Suite Installed!"
    echo "========================================"
    echo ""
    echo "To use it, open a new session and type:"
    echo ""
    echo "  /code-analyzer Review this code for security issues"
    echo ""
    echo "Or try these examples:"
    echo "  /code-analyzer Analyze src/auth.ts for vulnerabilities"
    echo "  /code-analyzer Check performance of this function"
    echo "  /code-analyzer Full review of the authentication module"
    echo ""
    echo "Platform: $platform"
    echo ""
}

# Main installation
main() {
    echo "========================================"
    echo "  Code Analyzer Suite Installer"
    echo "========================================"
    echo ""

    # Parse arguments
    local platform=""
    local project_level="false"
    local dry_run="false"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --platform)
                platform="$2"
                shift 2
                ;;
            --project)
                project_level="true"
                shift
                ;;
            --dry-run)
                dry_run="true"
                shift
                ;;
            --all)
                platform="all"
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --platform <name>  Install to specific platform"
                echo "  --project          Install to project-level path"
                echo "  --dry-run          Show what would be installed"
                echo "  --all              Install to all detected platforms"
                echo "  -h, --help         Show this help"
                echo ""
                echo "Supported platforms:"
                echo "  claude, copilot, cursor, windsurf, trae,"
                echo "  cline, roo, goose, opencode, gemini, kiro"
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Detect platform if not specified
    if [[ -z "$platform" ]]; then
        platform=$(detect_platform)
        info "Auto-detected platform: $platform"
    fi

    # Handle --all
    if [[ "$platform" == "all" ]]; then
        local platforms=("claude" "copilot" "cursor" "windsurf" "trae" "cline" "roo" "goose" "opencode" "gemini" "kiro")
        for p in "${platforms[@]}"; do
            local path=$(get_install_path "$p" "$project_level")
            if [[ "$dry_run" == "true" ]]; then
                info "[DRY-RUN] Would install to: $path"
            else
                install_skill "$path" "$p"
                adapt_format "$path" "$p"
            fi
        done
        success "Installed to all platforms!"
        exit 0
    fi

    # Get install path
    local target_path=$(get_install_path "$platform" "$project_level")

    if [[ "$dry_run" == "true" ]]; then
        info "[DRY-RUN] Would install to: $target_path"
        exit 0
    fi

    # Install
    install_skill "$target_path" "$platform"

    # Create universal symlink
    create_universal_symlink "$target_path"

    # Format adaptation
    adapt_format "$target_path" "$platform"

    # Print activation instructions
    print_activation "$platform"
}

main "$@"
