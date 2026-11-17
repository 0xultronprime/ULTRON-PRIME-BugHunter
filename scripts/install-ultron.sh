#!/usr/bin/env bash
# =====================================================================
# install-ultron.sh — One-click installer for ULTRON PRIME BugHunter
#
# Installs (macOS / Linux):
#   - skills/* (86: 83 original + 3 ULTRON PRIME) → ~/.claude/skills/
#     and, when detected or forced, ~/.agents/skills/ (Codex),
#     ~/.hermes/skills/ (Hermes), ~/.gemini/config/skills/ (AntiGravity)
#   - commands/*.md → ~/.claude/commands/
#   - ultron CLI → ~/.local/bin/ultron (symlink to ultron.py + ultron/ package)
#   - cbh CLI is left untouched — `cbh` keeps working as before.
#
# Flags: --all (detect all harnesses) --agents --hermes --antigravity
#        --no-shell (don't add ~/.local/bin to PATH in shell rc)
#        --uninstall (remove only this bundle's footprint)
# Idempotent. Requires: bash, python3. No network calls.
# =====================================================================
set -e
REPO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
BUNDLE="ultron-prime-bughunter"
MANIFEST_DIR="$HOME/.claude/.skill-manifests"
MANIFEST="$MANIFEST_DIR/$BUNDLE.txt"
BIN_DIR="$HOME/.local/bin"
DO_ALL=0; DO_AGENTS=0; DO_HERMES=0; DO_ANTIGRAVITY=0; DO_UNINSTALL=0; NO_SHELL=0
while [ $# -gt 0 ]; do
  case "$1" in
    --all) DO_ALL=1 ;;
    --agents) DO_AGENTS=1 ;;
    --hermes) DO_HERMES=1 ;;
    --antigravity) DO_ANTIGRAVITY=1 ;;
    --no-shell) NO_SHELL=1 ;;
    --uninstall) DO_UNINSTALL=1 ;;
    -h|--help) sed -n '2,/^# ===/p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $1 (try --help)" >&2; exit 2 ;;
  esac
  shift
done

if [ "$DO_UNINSTALL" = 1 ]; then
  if [ -f "$MANIFEST" ]; then
    while IFS= read -r f; do [ -n "$f" ] && rm -rf "$f"; done < "$MANIFEST"
    rm -f "$MANIFEST" "$BIN_DIR/ultron"
    echo "ULTRON PRIME BugHunter uninstalled."
  else
    echo "No manifest at $MANIFEST — nothing tracked to uninstall."
  fi
  exit 0
fi

mkdir -p "$MANIFEST_DIR" "$BIN_DIR"
: > "$MANIFEST"
install_skills_to() {
  local dest="$1"
  mkdir -p "$dest"
  for d in "$REPO_DIR"/skills/*/; do
    name="$(basename "$d")"
    if [ -f "$dest/$name/SKILL.md" ] && cmp -s "$d/SKILL.md" "$dest/$name/SKILL.md"; then continue; fi
    rm -rf "$dest/$name"; cp -r "$d" "$dest/$name"
    echo "$dest/$name" >> "$MANIFEST"
  done
  echo "  skills -> $dest"
}

echo "ULTRON PRIME BugHunter — installing..."
install_skills_to "$HOME/.claude/skills"
mkdir -p "$HOME/.claude/commands"
cp "$REPO_DIR"/commands/*.md "$HOME/.claude/commands/" 2>/dev/null || true
echo "$HOME/.claude/commands" >> "$MANIFEST"
[ "$DO_AGENTS" = 1 ] || [ "$DO_ALL" = 1 ] && { [ "$DO_AGENTS" = 1 ] || [ -d "$HOME/.agents" ] && install_skills_to "$HOME/.agents/skills"; }
[ "$DO_HERMES" = 1 ] || [ "$DO_ALL" = 1 ] && { [ "$DO_HERMES" = 1 ] || [ -d "$HOME/.hermes" ] && install_skills_to "$HOME/.hermes/skills"; }
[ "$DO_ANTIGRAVITY" = 1 ] || [ "$DO_ALL" = 1 ] && { [ "$DO_ANTIGRAVITY" = 1 ] || [ -d "$HOME/.gemini" ] && install_skills_to "$HOME/.gemini/config/skills"; }

# ultron CLI: symlink the ultron.py entry point; the ultron/ package sits next to it.
ln -sf "$REPO_DIR/ultron.py" "$BIN_DIR/ultron"
chmod +x "$REPO_DIR/ultron.py"
echo "$BIN_DIR/ultron" >> "$MANIFEST"
echo "  ultron CLI -> $BIN_DIR/ultron"

if [ "$NO_SHELL" = 0 ]; then
  for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    [ -f "$rc" ] || continue
    grep -q '.local/bin' "$rc" 2>/dev/null || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$rc"
  done
  echo "  PATH: ~/.local/bin added to shell rc (if missing)"
fi
echo ""
echo "Done. Verify with:"
echo "  ultron version    # or: $BIN_DIR/ultron version"
echo "  ultron skills     # should list 86 skills"
echo "  ultron triage sample-findings.json"
echo "  ultron report sample-findings.json --out sample-report.html"
echo "Original cbh CLI is untouched: cbh --help"
