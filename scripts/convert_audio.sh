#!/bin/bash
# convert_audio.sh — WAV → MP3 轉換 (ffmpeg)
# Usage: bash scripts/convert_audio.sh chapter-1.wav
#        bash scripts/convert_audio.sh --batch /path/to/wavs/

set -e

BITRATE="128k"
OUTDIR=""

convert_one() {
    local input="$1"
    if [[ ! -f "$input" ]]; then
        echo "❌ 檔案唔存在: $input"
        return 1
    fi

    local basename=$(basename "$input" .wav)
    basename=$(basename "$basename" .WAV)
    local output="${OUTDIR:-$(dirname "$input")}/${basename}.mp3"

    echo "🎵 轉換中: $input → $output"
    ffmpeg -y -i "$input" -codec:a libmp3lame -b:a "$BITRATE" -q:a 2 "$output" 2>&1 | tail -1

    local in_size=$(du -h "$input" | cut -f1)
    local out_size=$(du -h "$output" | cut -f1)
    echo "✅ 完成: ${in_size} → ${out_size} (${output})"
}

if [[ "$1" == "--batch" ]]; then
    SRC_DIR="${2:-.}"
    OUTDIR="${3:-$SRC_DIR}"
    shopt -s nullglob
    files=("$SRC_DIR"/*.wav "$SRC_DIR"/*.WAV)
    if [[ ${#files[@]} -eq 0 ]]; then
        echo "❌ 搵唔到 WAV 檔案喺: $SRC_DIR"
        exit 1
    fi
    echo "📂 批次轉換 ${#files[@]} 個檔案..."
    for f in "${files[@]}"; do
        convert_one "$f"
    done
    echo "✅ 全部完成！"
elif [[ -n "$1" ]]; then
    convert_one "$1"
else
    echo "Usage:"
    echo "  bash scripts/convert_audio.sh <file.wav>         # 轉換單個"
    echo "  bash scripts/convert_audio.sh --batch <dir>      # 批次轉換"
    exit 1
fi
