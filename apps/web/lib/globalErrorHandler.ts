/**
 * Global Error Handler for API Responses
 * Manages toast notifications for 4xx/5xx errors
 */

// Global toast handler - will be set by the app
let globalToastHandler: ((message: string, type: 'error' | 'warning') => void) | null = null;

export const setGlobalToastHandler = (handler: (message: string, type: 'error' | 'warning') => void) => {
  globalToastHandler = handler;
};

export const handleApiError = (response: Response, errorMessage?: string) => {
  if (!globalToastHandler) return;

  const status = response.status;
  
  if (status >= 400 && status < 500) {
    // Client errors (4xx)
    let message = errorMessage || 'Request failed';
    
    switch (status) {
      case 400:
        message = 'Invalid request data';
        break;
      case 401:
        message = 'Authentication required';
        break;
      case 403:
        message = 'Access denied';
        break;
      case 404:
        message = 'Resource not found';
        break;
      case 409:
        message = 'Conflict with existing data';
        break;
      case 422:
        message = 'Validation error';
        break;
      default:
        message = errorMessage || 'Request failed';
    }
    
    globalToastHandler(message, 'warning');
  } else if (status >= 500) {
    // Server errors (5xx)
    const message = 'Server error occurred. Please try again later.';
    globalToastHandler(message, 'error');
  }
};

export const handleNetworkError = (error: Error) => {
  if (!globalToastHandler) return;
  
  globalToastHandler('Network error. Please check your connection.', 'error');
};