'use client';

import { useEffect, useState } from 'react';

const STORAGE_KEY = 'openNemesisUserId';

export function useUserId(): string {
  const [userId, setUserId] = useState<string>('');

  useEffect(() => {
    let storedId = localStorage.getItem(STORAGE_KEY);
    
    if (!storedId) {
      storedId = 'user-' + Math.random().toString(36).substring(2, 11);
      localStorage.setItem(STORAGE_KEY, storedId);
    }
    
    setUserId(storedId);
  }, []);

  return userId;
}