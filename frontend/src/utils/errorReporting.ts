import { Alert, Linking } from 'react-native';
import { ErrorUtils } from 'react-native';

let isHandlingError = false;

const sendBugReport = async (errorType: string, errorMessage: string, stackTrace?: string) => {
  const subject = encodeURIComponent('Sock Graveyard App Error Report');
  const body = encodeURIComponent(
    `Error Report\n\n` +
    `Error Type: ${errorType}\n\n` +
    `Error: ${errorMessage}\n\n` +
    `Stack Trace:\n${stackTrace || 'No stack trace available'}\n\n` +
    `Timestamp: ${new Date().toISOString()}\n` +
    `User Agent: React Native App\n`
  );
  
  const mailtoUrl = `mailto:socks@arnodece.com?subject=${subject}&body=${body}`;
  
  try {
    const canOpen = await Linking.canOpenURL(mailtoUrl);
    if (canOpen) {
      await Linking.openURL(mailtoUrl);
    } else {
      Alert.alert(
        'Email Not Available',
        'Please send a bug report to: socks@arnodece.com'
      );
    }
  } catch (err) {
    Alert.alert(
      'Error',
      'Could not open email client. Please email socks@arnodece.com manually.'
    );
  }
};

const showErrorAlert = (errorType: string, errorMessage: string, stackTrace?: string) => {
  if (isHandlingError) return;
  isHandlingError = true;

  Alert.alert(
    'Unexpected Error',
    'The app encountered an unexpected error. Would you like to send a bug report?',
    [
      {
        text: 'Cancel',
        style: 'cancel',
        onPress: () => {
          isHandlingError = false;
        },
      },
      {
        text: 'Send Report',
        onPress: async () => {
          await sendBugReport(errorType, errorMessage, stackTrace);
          isHandlingError = false;
        },
      },
    ],
    { 
      cancelable: true,
      onDismiss: () => {
        isHandlingError = false;
      },
    }
  );
};

export const setupGlobalErrorHandlers = () => {
  // Handle unhandled promise rejections
  const originalPromiseRejectionHandler = global.Promise.prototype.catch;
  
  // Setup tracking for unhandled rejections
  const handleUnhandledRejection = (reason: any, promise: Promise<any>) => {
    console.error('Unhandled Promise Rejection:', reason);
    
    const errorMessage = reason?.message || reason?.toString() || 'Unknown error';
    const stackTrace = reason?.stack || '';
    
    showErrorAlert('Unhandled Promise Rejection', errorMessage, stackTrace);
  };

  // Listen for unhandled promise rejections
  const rejectionHandler = (event: any) => {
    handleUnhandledRejection(event.reason, event.promise);
  };

  if (typeof window !== 'undefined' && window.addEventListener) {
    window.addEventListener('unhandledrejection', rejectionHandler);
  }

  // Handle global JavaScript errors
  const defaultErrorHandler = ErrorUtils.getGlobalHandler();
  
  ErrorUtils.setGlobalHandler((error: Error, isFatal?: boolean) => {
    console.error('Global Error Handler:', error, 'isFatal:', isFatal);
    
    const errorMessage = error.message || error.toString();
    const stackTrace = error.stack || '';
    
    if (isFatal) {
      showErrorAlert('Fatal Error', errorMessage, stackTrace);
    } else {
      showErrorAlert('JavaScript Error', errorMessage, stackTrace);
    }
    
    // Call the default handler to ensure the error is still logged
    defaultErrorHandler(error, isFatal);
  });

  console.log('Global error handlers initialized');
};
