'use client';

import { useCategories } from '@/hooks/useCategories';
import { Search, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

export default function Home() {
  const {
    categories,
    selectedCategory,
    isLoading,
    isSearching,
    isProcessing,
    error,
    searchQuery,
    selectCategory,
    clearSelection,
    setSearchQuery,
  } = useCategories();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
  };

  const handleCategoryClick = async (category: typeof categories[0]) => {
    if (isProcessing) return;
    
    if (selectedCategory?.id === category.id) {
      clearSelection();
    } else {
      await selectCategory(category);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <form onSubmit={handleSearch} className="mb-6">
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Semantic search"
                className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                disabled={isLoading}
              />
              <button
                type="submit"
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                disabled={isSearching}
              >
                {isSearching ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Search className="w-5 h-5" />
                )}
              </button>
            </div>
          </form>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
              <span className="ml-2 text-gray-600">Loading categories...</span>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {categories.map((category) => {
                const isSelected = selectedCategory?.id === category.id;
                const isActive = isSelected;
                
                return (
                  <button
                    key={category.id}
                    onClick={() => handleCategoryClick(category)}
                    disabled={isProcessing}
                    className={`${
                      isActive ? 'bg-green-500' : 'bg-gray-400'
                    } text-white p-4 rounded-lg hover:opacity-90 transition-all duration-200 text-left font-medium relative disabled:opacity-50 disabled:cursor-not-allowed`}
                    title={category.description}
                  >
                    <div className="flex items-center justify-between">
                      <span>{category.title}</span>
                      {isSelected && (
                        <CheckCircle className="w-5 h-5 ml-2 flex-shrink-0" />
                      )}
                      {isProcessing && selectedCategory?.id === category.id && (
                        <Loader2 className="w-5 h-5 ml-2 flex-shrink-0 animate-spin" />
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          )}

          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center">
              <AlertCircle className="w-5 h-5 text-red-500 mr-2 flex-shrink-0" />
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}

          <div className="mt-6 text-gray-600">
            <p className="text-green-600 font-medium mb-2">
              {selectedCategory ? `Selected: ${selectedCategory.title}` : 'Add description on'}
            </p>
            <p className="mb-4">
              {selectedCategory 
                ? selectedCategory.description 
                : 'Linked to the data, or the active cam'
              }
            </p>
            {selectedCategory && (
              <div className="mt-3">
                <p className="text-sm text-gray-500 mb-2">Tags:</p>
                <div className="flex flex-wrap gap-2">
                  {selectedCategory.tags.map((tag, index) => (
                    <span 
                      key={index}
                      className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
