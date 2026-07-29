#!/usr/bin/env bash
#
# Cross-platform installer for parallel-decomposer-skill
# Supports: Claude Code, GitHub Copilot, Cursor, Windsurf, Cline,
#           Trae, Gemini CLI, Goose, OpenCode, Roo Code, and more.
#

set -euo pipefail

SKILL_NAME="parallel-decomposer-skill"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY_RUN=false
PLATFORM=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Install ${SKILL_NAME} to your agent tool's skill directory.

OPTIONS:
    -p, --platform <name>   Install to specific platform (claude, copilot, cursor, etc.)
    -a, --all               Install to all detected platforms
    -d, --dry-run           Show what would be done without doing it
    -h, --help              Show this help message

SUPPORTED PLATFORMS:
    claude, copilot, cursor, windsurf, cline, trae,
    gemini, goose, opencode, roo-code, kiro, codex

EXAMPLES:
    $0                      Auto-detect and install
    $0 --platform claude    Install to Claude Code only
    $0 --all                Install everywhere detected
    $0 --dry-run            Preview installation plan
EOF
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

detect_platforms() {
    local platforms=""

    if [[ -d "$HOME/.claude" ]]; then
        platforms="${platforms}claude "
    fi
    if [[ -d "$HOME/.copilot" ]]; then
        platforms="${platforms}copilot "
    fi
    if [[ -d ".github" ]] || [[ -d "$HOME/.github" ]]; then
        platforms="${platforms}copilot-project "
    fi
    if [[ -d ".cursor" ]]; then
        platforms="${platforms}cursor "
    fi
    if [[ -d "$HOME/.codeium/windsurf" ]] || [[ -d ".windsurf" ]]; then
        platforms="${platforms}windsurf "
    fi
    if [[ -d "$HOME/.cline" ]] || [[ -d ".clinerules" ]]; then
        platforms="${platforms}cline "
    fi
    if [[ -d ".trae" ]] || [[ -d "$HOME/.trae" ]]; then
        platforms="${platforms}trae "
    fi
    if [[ -d "$HOME/.gemini" ]]; then
        platforms="${platforms}gemini "
    fi
    if [[ -d "$HOME/.config/goose" ]]; then
        platforms="${platforms}goose "
    fi
    if [[ -d "$HOME/.config/opencode" ]] || [[ -d ".opencode" ]]; then
        platforms="${platforms}opencode "
    fi
    if [[ -d "$HOME/.roo" ]] || [[ -d ".roo" ]]; then
        platforms="${platforms}roo-code "
    fi
    if [[ -d "$HOME/.kiro" ]] || [[ -d ".kiro" ]]; then
        platforms="${platforms}kiro "
    fi
    if [[ -d "$HOME/.agents" ]]; then
        platforms="${platforms}codex "
    fi

    echo "$platforms"
}

install_to_claude() {
    local target="$HOME/.claude/skills/$SKILL_NAME"
    if [[ "$DRY_RUN" == true ]]; then
        log_info "Would install to: $target"
        return
    fi
    mkdir -p "$HOME/.claude/skills"
    cp -R "$SCRIPT_DIR" "$target"
    log_info "Installed to Claude Code: $target"
}

install_to_copilot() {
    local target="$HOME/.copilot/skills/$SKILL_NAME"
    if [[ "$DRY_RUN" == true ]]; then
        log_info "Would install to: $target"
        return
    fi
    mkdir -p "$HOME/.copilot/skills"
    cp -R "$SCRIPT_DIR" "$target"
    log_info "Installed to GitHub Copilot: $target"
}

install_to_copilot_project() {
    local target=".github/skills/$SKILL_NAME"
    if [[ "$DRY_RUN" == true ]]; then
        log_info "Would install to: $target"
        return
    fi
    mkdir -p ".github/skills"
    cp -R "$SCRIPT_DIR" "$target"
    log_info "Installed to VS Code Copilot (project): $target"
}

install_to_cursor() {
    local target=".cursor/skills/$SKILL_NAME"
    if [[ "$DRY_RUN" == true ]]; then
        log_info "Would install to: $target"
        return
    fi
    mkdir -p ".cursor/skills"
    cp -R "$SCRIPT_DIR" "$target"
    # Also create .mdc for Cursor native format
    cat > ".cursor/skills/$SKILL_NAME/$SKILL_NAME.mdc" <<EOF
---
description: Decompose complex tasks into parallel subtasks for multi-agent execution
globs: *
alwaysApply: true
---
# /parallel-decomposer

You are an expert task decomposition specialist. Your job is to analyze complex tasks and break them into 3-7 independent subtasks that can be executed in parallel by multiple agents.

## Trigger

User invokes \`/parallel-decomposer\` followed by their complex task.

## Core Workflow

1. Analyze the task (domain, objectives, constraints, context, output format)
2. Identify decomposition dimensions (by aspect, component, stage, audience, etc.)
3. Check for dependencies between potential subtasks
4. Generate structured subtask cards with copy-paste ready prompts
5. Provide integration template for merging parallel results

## Output Rules

- Always include full context in each subtask card
- Never create dependent subtasks without Phase 1/2 labeling
- Complexity estimates: Low (<30min), Medium (30-90min), High (>90min)
- Suggest optimal worker count
- Include copy-paste ready prompts
- Flag risks when parallelization might hurt quality
EOF
    log_info "Installed to Cursor (project): $target"
}

install_to_windsurf() {
    local target=""
    if [[ -d "$HOME/.codeium/windsurf" ]]; then
        target="$HOME/.codeium/windsurf/skills/$SKILL_NAME"
        mkdir -p "$HOME/.codeium/windsurf/skills"
    else
        target=".windsurf/rules/$SKILL_NAME"
        mkdir -p ".windsurf/rules"
    fi
    if [[ "$DRY_RUN" == true ]]; then
        log_info "Would install to: $target"
        return
    fi
    cp -R "$SCRIPT_DIR" "$target"
    # Create plain .md rule (under 6000 chars)
    cat > "$target/rule.md" <<'EOF'
# parallel-decomposer

Decompose complex tasks into parallel subtasks for multi-agent execution.

When user invokes `/parallel-decomposer` or asks to break down a task for parallel work:

1. Analyze task: domain, objectives, constraints, context, output format
2. Identify decomposition dimension (aspect, component, stage, audience, methodology)
3. Check dependencies - ensure subtasks are independent
4. Generate 3-7 subtask cards with: title, complexity, context, prompt, output format
5. Provide integration template for merging results

Rules:
- Include full context in each card (agents run in isolation)
- Estimate complexity realistically
- Suggest optimal worker count
- Flag risks when parallelization hurts quality
- Never create dependent subtasks without explicit Phase labeling
EOF
    log_info "Installed to Windsurf: $target"
}

install_to_cline() {
    local target="$HOME/.cline/skills/$SKILL_NAME"
    if [[ -d ".clinerules" ]]; then
        target=".clinerules/skills/$SKILL_NAME"
        mkdir -p ".clinerules/skills"
    else
        mkdir -p "$HOME/.cline/skills"
    fi
    if [[ "$DRY_RUN" == true ]]; then
        log_info "Would install to: $target"
        return
    fi
    cp -R "$SCRIPT_DIR" "$target"
    log_info "Installed to Cline: $target"
}

install_to_trae() {
    local target=".trae/rules/$SKILL_NAME"
    if [[ "$DRY_RUN" == true ]]; then
        log_info "Would install to: $target"
        return
    fi
    mkdir -p ".trae/rules"
    cp -R "$SCRIPT_DIR" "$target"
    # Create Trae native format
    cat > ".trae/rules/$SKILL_NAME.md" <<EOF
---
type: Always
---
# /parallel-decomposer

You are an expert task decomposition specialist. Analyze complex tasks and break them into 3-7 independent subtasks for parallel execution.

## Workflow

1. **Analyze**: Understand domain, objectives, constraints, context
2. **Decompose**: Choose dimension (aspect, component, stage, audience)
3. **Check Dependencies**: Ensure independence
4. **Generate Cards**: Structured subtask cards with prompts
5. **Integration Template**: Provide merge instructions

## Rules

- Full context in each card
- Realistic complexity estimates
- Optimal worker count suggestion
- Risk warnings for unsuitable tasks
- No hidden dependencies
EOF
    log_info "Installed to Trae (project): $target"
}

install_to_gemini() {
    local target="$HOME/.gemini/skills/$SKILL_NAME"
    if [[ "$DRY_RUN" == true ]]; then
        log_info "Would install to: $target"
        return
    fi
    mkdir -p "$HOME/.gemini/skills"
    cp -R "$SCRIPT_DIR" "$target"
    log_info "Installed to Gemini CLI: $target"
}

install_to_goose() {
    local target="$HOME/.config/goose/skills/$SKILL_NAME"
    if [[ "$DRY_RUN" == true ]]; then
        log_info "Would install to: $target"
        return
    fi
    mkdir -p "$HOME/.config/goose/skills"
    cp -R "$SCRIPT_DIR" "$target"
    log_info "Installed to Goose: $target"
}

install_to_opencode() {
    local target="$HOME/.config/opencode/skills/$SKILL_NAME"
    if [[ -d ".opencode" ]]; then
        target=".opencode/skills/$SKILL_NAME"
        mkdir -p ".opencode/skills"
    else
        mkdir -p "$HOME/.config/opencode/skills"
    fi
    if [[ "$DRY_RUN" == true ]]; then
        log_info "Would install to: $target"
        return
    fi
    cp -R "$SCRIPT_DIR" "$target"
    log_info "Installed to OpenCode: $target"
}

install_to_roo_code() {
    local target="$HOME/.roo/skills/$SKILL_NAME"
    if [[ -d ".roo" ]]; then
        target=".roo/skills/$SKILL_NAME"
        mkdir -p ".roo/skills"
    else
        mkdir -p "$HOME/.roo/skills"
    fi
    if [[ "$DRY_RUN" == true ]]; then
        log_info "Would install to: $target"
        return
    fi
    cp -R "$SCRIPT_DIR" "$target"
    log_info "Installed to Roo Code: $target"
}

install_to_kiro() {
    local target="$HOME/.kiro/skills/$SKILL_NAME"
    if [[ -d ".kiro" ]]; then
        target=".kiro/skills/$SKILL_NAME"
        mkdir -p ".kiro/skills"
    else
        mkdir -p "$HOME/.kiro/skills"
    fi
    if [[ "$DRY_RUN" == true ]]; then
        log_info "Would install to: $target"
        return
    fi
    cp -R "$SCRIPT_DIR" "$target"
    log_info "Installed to Kiro: $target"
}

install_to_codex() {
    local target="$HOME/.agents/skills/$SKILL_NAME"
    if [[ "$DRY_RUN" == true ]]; then
        log_info "Would install to: $target"
        return
    fi
    mkdir -p "$HOME/.agents/skills"
    cp -R "$SCRIPT_DIR" "$target"
    log_info "Installed to universal path: $target"
}

install_platform() {
    local platform="$1"
    case "$platform" in
        claude) install_to_claude ;;
        copilot) install_to_copilot ;;
        copilot-project) install_to_copilot_project ;;
        cursor) install_to_cursor ;;
        windsurf) install_to_windsurf ;;
        cline) install_to_cline ;;
        trae) install_to_trae ;;
        gemini) install_to_gemini ;;
        goose) install_to_goose ;;
        opencode) install_to_opencode ;;
        roo-code) install_to_roo_code ;;
        kiro) install_to_kiro ;;
        codex) install_to_codex ;;
        *)
            log_error "Unknown platform: $platform"
            return 1
            ;;
    esac
}

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -p|--platform)
                PLATFORM="$2"
                shift 2
                ;;
            -a|--all)
                PLATFORM="all"
                shift
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done

    log_info "Installing ${SKILL_NAME}..."

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN MODE - No changes will be made"
    fi

    if [[ -n "$PLATFORM" ]]; then
        if [[ "$PLATFORM" == "all" ]]; then
            local detected
            detected="$(detect_platforms)"
            if [[ -z "$detected" ]]; then
                log_warn "No platforms detected"
                exit 1
            fi
            log_info "Installing to all detected platforms: $detected"
            for p in $detected; do
                install_platform "$p"
            done
        else
            install_platform "$PLATFORM"
        fi
    else
        # Auto-detect
        local detected
        detected="$(detect_platforms)"
        if [[ -z "$detected" ]]; then
            log_warn "No supported platforms detected"
            log_info "Install manually by copying this directory to your tool's skills folder"
            log_info "Or specify platform with: $0 --platform <name>"
            exit 1
        fi

        # Install to first detected platform
        local first
        first="$(echo "$detected" | awk '{print $1}')"
        log_info "Auto-detected platforms: $detected"
        log_info "Installing to: $first (use --all for all platforms)"
        install_platform "$first"

        # Always install to universal path
        install_to_codex
    fi

    echo ""
    log_info "Installation complete!"
    echo ""
    echo "To use the skill, open a new session and type:"
    echo ""
    echo "  /parallel-decomposer Analyze this codebase for security and performance"
    echo ""
}

main "$@"
