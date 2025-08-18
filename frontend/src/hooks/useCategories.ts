'use client';

import { useState, useEffect, useCallback } from 'react';

export interface Category {
  id: number;
  title: string;
  description: string;
  tags: string[];
}

export interface UseCategoriesReturn {
  categories: Category[];
  selectedCategory: Category | null;
  isLoading: boolean;
  isSearching: boolean;
  isProcessing: boolean;
  error: string | null;
  searchQuery: string;
  searchCategories: (query: string) => Promise<void>;
  selectCategory: (category: Category) => Promise<void>;
  clearSelection: () => void;
  setSearchQuery: (query: string) => void;
}

export function useCategories(): UseCategoriesReturn {
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const searchCategories = useCallback(async (query: string) => {
    setIsSearching(true);
    setError(null);
    
    try {
      const url = new URL('/api/categories', window.location.origin);
      if (query.trim()) {
        url.searchParams.set('q', query.trim());
      }
      
      const response = await fetch(url.toString());
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        setCategories(result.data);
      } else {
        throw new Error(result.error || 'Failed to fetch categories');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while searching');
      console.error('Search error:', err);
    } finally {
      setIsSearching(false);
    }
  }, []);

  useEffect(() => {
    const loadInitialCategories = async () => {
      setIsLoading(true);
      await searchCategories('');
      setIsLoading(false);
    };
    
    loadInitialCategories();
  }, [searchCategories]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchQuery !== '') {
        searchCategories(searchQuery);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery, searchCategories]);

  const selectCategory = useCallback(async (category: Category) => {
    setIsProcessing(true);
    setError(null);
    
    try {
      const response = await fetch('/api/categories/select', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          categoryId: category.id,
          categoryTitle: category.title,
          additionalData: {
            description: category.description,
            tags: category.tags,
            timestamp: new Date().toISOString()
          }
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        setSelectedCategory(category);
        console.log('Category selection processed:', result.data);
      } else {
        throw new Error(result.error || 'Failed to process category selection');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while selecting category');
      console.error('Selection error:', err);
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedCategory(null);
    setError(null);
  }, []);

  return {
    categories,
    selectedCategory,
    isLoading,
    isSearching,
    isProcessing,
    error,
    searchQuery,
    searchCategories,
    selectCategory,
    clearSelection,
    setSearchQuery,
  };
}