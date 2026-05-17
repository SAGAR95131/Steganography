import { CapacitorConfig } from '@capacitor/cli';

// Default to Android emulator localhost mapping (10.0.2.2) on port 5000.
// Change url to your LAN IP or HTTPS domain for real devices/production.
const config: CapacitorConfig = {
  appId: 'com.cybercloak.app',
  appName: 'CyberCloak',
  webDir: 'www',
  server: {
    url: 'http://10.0.2.2:5000',
    cleartext: true
  },
  android: {
    allowMixedContent: true
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 1200,
      launchAutoHide: true,
      backgroundColor: '#0f0f23',
      androidSplashResourceName: 'splash',
      androidScaleType: 'CENTER_CROP',
      showSpinner: false
    }
  }
};

export default config;


