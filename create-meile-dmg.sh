#!/bin/bash

create-dmg \
  --volname "Meile" \
  --volicon "icon.icns" \
  --background "meile.app.png" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "dist/Meile/Meile.app" 200 190 \
  --app-drop-link 600 185 \
  "Meile-v1.5.0.dmg" \
  "dist/Meile/"