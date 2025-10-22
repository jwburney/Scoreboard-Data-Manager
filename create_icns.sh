#!/bin/bash
# Script to create .icns file from PNG icons (Mac only)

echo "Creating .icns file for Mac..."

# Create iconset directory
mkdir -p pennant.iconset

# Copy images at required sizes
cp icon_16x16.png pennant.iconset/icon_16x16.png
cp icon_32x32.png pennant.iconset/icon_16x16@2x.png
cp icon_32x32.png pennant.iconset/icon_32x32.png
cp icon_64x64.png pennant.iconset/icon_32x32@2x.png
cp icon_128x128.png pennant.iconset/icon_128x128.png
cp icon_256x256.png pennant.iconset/icon_128x128@2x.png
cp icon_256x256.png pennant.iconset/icon_256x256.png
cp icon_512x512.png pennant.iconset/icon_256x256@2x.png
cp icon_512x512.png pennant.iconset/icon_512x512.png
cp icon_1024x1024.png pennant.iconset/icon_512x512@2x.png

# Convert to icns (Mac only command)
iconutil -c icns pennant.iconset

echo "Created pennant.icns"
echo "You can now delete the pennant.iconset folder if you wish"
