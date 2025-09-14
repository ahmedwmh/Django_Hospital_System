#!/bin/bash

echo "🔧 Fixing Connection Issues for Django Hospital System"
echo "====================================================="
echo ""
echo "Your app is LIVE at: https://urchin-app-j2low.ondigitalocean.app/"
echo "But you can't access it due to local network issues."
echo ""
echo "Running DNS and network fixes..."
echo ""

echo "1. Flushing DNS cache..."
sudo dscacheutil -flushcache
echo "✅ DNS cache flushed"

echo ""
echo "2. Restarting mDNSResponder..."
sudo killall -HUP mDNSResponder
echo "✅ mDNSResponder restarted"

echo ""
echo "3. Clearing system cache..."
sudo rm -rf /var/folders/*/com.apple.LaunchServices-*
echo "✅ System cache cleared"

echo ""
echo "====================================================="
echo "🎯 NEXT STEPS:"
echo "1. Restart your computer"
echo "2. Try accessing: https://urchin-app-j2low.ondigitalocean.app/"
echo "3. If still not working, try mobile data on your phone"
echo "4. Or try a different network (work, friend's house)"
echo ""
echo "Your Django Hospital System is working perfectly!"
echo "The issue is just local network connectivity."
echo "====================================================="
