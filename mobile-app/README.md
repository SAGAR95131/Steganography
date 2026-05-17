# CyberCloak Android (Capacitor)

Configure URL in `capacitor.config.ts`:
- Emulator: `http://10.0.2.2:5000`
- Real device: `http://YOUR_PC_LAN_IP:5000`
- Production: `https://your-domain`

Build:
```
cd mobile-app
npm install
npx cap add android
npx cap copy && npx cap sync
npx cap open android
```
In Android Studio: Build > Build Bundle(s)/APK(s) > Build APK(s).
Copy APK to `C:\Users\rahul\Desktop\IGM\static\downloads\CyberCloak-Android.apk`.
Open `/mobile` and tap Download APK.

