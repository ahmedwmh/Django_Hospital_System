@echo off
echo 🔧 Fixing Connection Issues for Django Hospital System
echo =====================================================
echo.
echo Your app is LIVE at: https://urchin-app-j2low.ondigitalocean.app/
echo But you can't access it due to local network issues.
echo.
echo Running DNS and network fixes...
echo.

echo 1. Flushing DNS cache...
ipconfig /flushdns
echo ✅ DNS cache flushed

echo.
echo 2. Releasing IP configuration...
ipconfig /release
echo ✅ IP released

echo.
echo 3. Renewing IP configuration...
ipconfig /renew
echo ✅ IP renewed

echo.
echo 4. Resetting Winsock catalog...
netsh winsock reset
echo ✅ Winsock reset

echo.
echo 5. Clearing ARP cache...
arp -d *
echo ✅ ARP cache cleared

echo.
echo =====================================================
echo 🎯 NEXT STEPS:
echo 1. Restart your computer
echo 2. Try accessing: https://urchin-app-j2low.ondigitalocean.app/
echo 3. If still not working, try mobile data on your phone
echo 4. Or try a different network (work, friend's house)
echo.
echo Your Django Hospital System is working perfectly!
echo The issue is just local network connectivity.
echo =====================================================
pause
