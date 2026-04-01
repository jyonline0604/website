#!/bin/bash
# Move the latest generated image to target path
TARGET="$1"
LATEST=$(ls -t /home/openclaw/.openclaw/media/tool-image-generation/image-1---*.png | head -1)
if [ -n "$LATEST" ]; then
    mv "$LATEST" "$TARGET"
    echo "Moved: $LATEST -> $TARGET"
else
    echo "No image found!"
fi
