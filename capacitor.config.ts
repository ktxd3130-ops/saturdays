import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.kendalldale.saturdays',
  appName: 'Saturdays',
  webDir: 'www',
  backgroundColor: '#f6f8fc',
  ios: {
    backgroundColor: '#f6f8fc',
    contentInset: 'always',
  },
  plugins: {
    LocalNotifications: {
      // Tinted to match the app's indigo accent on the lock screen / banner.
      iconColor: '#4f46e5',
    },
  },
};

export default config;
