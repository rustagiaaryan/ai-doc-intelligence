// FILE: services/web-frontend/src/utils/errorHandler.ts

/**
 * Format API error response for user display
 * Handles both simple error messages and Pydantic validation error arrays
 */
export function formatApiError(error: any, fallbackMessage: string = 'An error occurred'): string {
  // If no error response, return fallback
  if (!error?.response?.data) {
    return fallbackMessage;
  }

  const { detail } = error.response.data;

  // If detail is a string, return it directly
  if (typeof detail === 'string') {
    return detail;
  }

  // If detail is an array of validation errors
  if (Array.isArray(detail)) {
    // Extract the first error message
    const firstError = detail[0];
    if (firstError && firstError.msg) {
      // Format: "Field 'fieldname': error message"
      const field = firstError.loc?.join('.') || 'Unknown field';
      return `${field}: ${firstError.msg}`;
    }
    return 'Validation error occurred';
  }

  // If detail is an object
  if (typeof detail === 'object') {
    return JSON.stringify(detail);
  }

  return fallbackMessage;
}
