#!/usr/bin/env bash
# Print the rendered master architecture page to PDF with headless Chrome (release workflow; also runs locally).
#   tools/build_pdf.sh <site-dir> <out.pdf>
set -euo pipefail
SITE="${1:?site dir (output of tools/site/build.mjs)}"
OUT="${2:?output pdf}"
CHROME=""
for c in google-chrome google-chrome-stable chromium chromium-browser "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"; do
  if command -v "$c" >/dev/null 2>&1 || [[ -x "$c" ]]; then CHROME="$c"; break; fi
done
[[ -n "$CHROME" ]] || { echo "Chrome or Chromium is required" >&2; exit 3; }
SITE="$(cd "$SITE" && pwd)"
PRINT="$SITE/print.html"
{
  echo '<!doctype html><html lang="en" data-theme="light"><head><meta charset="utf-8">'
  echo '<meta name="viewport" content="width=device-width, initial-scale=1">'
  echo '<style>@media print{.rail,.mobile-toc,.filter{display:none!important}main{margin-left:0!important}.block,.table-wrap,.diagram{overflow:visible!important}.block code{white-space:pre-wrap!important}h2,h3{break-after:avoid}figure,.block.wire,table{break-inside:avoid}}@page{size:A4;margin:14mm}</style>'
  echo '</head><body>'
  cat "$SITE/index.html"
  echo '<script src="https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"></script>'
  echo '<script>if(window.mermaid){mermaid.initialize({startOnLoad:false,theme:"neutral"});mermaid.run({querySelector:"pre.mermaid",suppressErrors:true});}</script>'
  echo '</body></html>'
} > "$PRINT"
mkdir -p "$(dirname "$OUT")"
"$CHROME" --headless --disable-gpu --no-sandbox --no-pdf-header-footer --virtual-time-budget=30000 \
  --run-all-compositor-stages-before-draw --print-to-pdf="$OUT" "file://$PRINT" 2>/dev/null || true   # success is judged by the output file below
rm -f "$PRINT"
[[ -s "$OUT" ]] || { echo "PDF was not produced" >&2; exit 1; }
echo "wrote $OUT ($(du -h "$OUT" | cut -f1))"
