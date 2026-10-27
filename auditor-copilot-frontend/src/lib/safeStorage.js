/**
 * Safe in-memory fallback for localStorage when access is denied by browser security policies
 * (e.g. Chrome incognito, third-party cookie restrictions, or iframe sandbox).
 */

const memoryStorage = new Map();

function checkStorageAvailability() {
  try {
    if (typeof window === "undefined") return false;
    const testKey = "__safe_storage_test__";
    window.localStorage.setItem(testKey, testKey);
    window.localStorage.removeItem(testKey);
    return true;
  } catch {
    return false;
  }
}

const hasNativeStorage = checkStorageAvailability();

export const safeStorage = {
  getItem: (key) => {
    try {
      if (hasNativeStorage) {
        return window.localStorage.getItem(key);
      }
    } catch {
      // Fall back to memory
    }
    return memoryStorage.has(key) ? memoryStorage.get(key) : null;
  },

  setItem: (key, value) => {
    try {
      if (hasNativeStorage) {
        window.localStorage.setItem(key, value);
        return;
      }
    } catch {
      // Fall back to memory
    }
    memoryStorage.set(key, String(value));
  },

  removeItem: (key) => {
    try {
      if (hasNativeStorage) {
        window.localStorage.removeItem(key);
        return;
      }
    } catch {
      // Fall back to memory
    }
    memoryStorage.delete(key);
  },

  clear: () => {
    try {
      if (hasNativeStorage) {
        window.localStorage.clear();
        return;
      }
    } catch {
      // Fall back to memory
    }
    memoryStorage.clear();
  },
};

export default safeStorage;

