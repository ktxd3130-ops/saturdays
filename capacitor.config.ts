import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.kendalldale.saturdays',
  appName: 'Saturdays',
  webDir: 'www',
  backgroundColor: '#0a0a0b',
  ios: {
    backgroundColor: '#0a0a0b',
    contentInset: 'always',
  },
  plugins: {
    LocalNotifications: {
      // Tinted to match the app's amber accent on the lock screen / banner.
      iconColor: '#f0a04b',
    },
  },
};

export default config;
