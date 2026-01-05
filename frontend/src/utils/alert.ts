import { Alert as RNAlert, Platform } from 'react-native';

interface AlertButton {
  text: string;
  onPress?: () => void;
  style?: 'default' | 'cancel' | 'destructive';
}

class CrossPlatformAlert {
  alert(
    title: string,
    message?: string,
    buttons?: AlertButton[],
    options?: { cancelable?: boolean }
  ): void {
    if (Platform.OS === 'web') {
      // For web, use window.confirm or custom implementation
      const buttonTexts = buttons?.map(b => b.text).join(' / ') || 'OK';
      const fullMessage = message ? `${title}\n\n${message}` : title;
      
      if (buttons && buttons.length > 1) {
        // Multi-button alert - use confirm dialog
        const confirmed = window.confirm(fullMessage);
        
        // Find the appropriate button to call
        if (confirmed) {
          // Call the first non-cancel button
          const confirmButton = buttons.find(b => b.style !== 'cancel');
          confirmButton?.onPress?.();
        } else {
          // Call the cancel button
          const cancelButton = buttons.find(b => b.style === 'cancel');
          cancelButton?.onPress?.();
        }
      } else {
        // Single button alert - use alert dialog
        window.alert(fullMessage);
        buttons?.[0]?.onPress?.();
      }
    } else {
      // For mobile, use native Alert
      RNAlert.alert(title, message, buttons, options);
    }
  }
}

export const Alert = new CrossPlatformAlert();
