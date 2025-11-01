import React, { useState } from 'react'
import { useKnowledgeBase } from '@/hooks/useGitHubData'
import type { KnowledgeEntry } from '@/types'

const KNOWLEDGE_TYPES = [
  { id: 'all', label: 'All', icon: '📚' },
  { id: 'decision', label: 'Decisions', icon: '🎯' },
  { id: 'pattern', label: 'Patterns', icon: '🔄' },
  { id: 'learning', label: 'Learnings', icon: '💡' },
  { id: 'issue_resolution', label: 'Resolutions', icon: '🔧' },
  { id: 'best_practice', label: 'Best Practices', icon: '⭐' },
] as const

export const KnowledgeBase: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [activeFilter, setActiveFilter] = useState<string>('all')
  const [debouncedQuery, setDebouncedQuery] = useState('')

  // Debounce search query
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery)
    }, 500)

    return () => clearTimeout(timer)
  }, [searchQuery])

  const { data: entries = [], isLoading, error } = useKnowledgeBase(
    debouncedQuery.length >= 2 ? debouncedQuery : undefined
  )

  // Filter entries by type
  const filteredEntries = entries.filter((entry: KnowledgeEntry) =>
    activeFilter === 'all' || entry.knowledge_type === activeFilter
  )

  const getTypeIcon = (type: KnowledgeEntry['knowledge_type']) => {
    return KNOWLEDGE_TYPES.find(t => t.id === type)?.icon || '📄'
  }

  const getTypeColor = (type: KnowledgeEntry['knowledge_type']) => {
    switch (type) {
      case 'decision':
        return 'bg-purple-100 text-purple-800 border-purple-200'
      case 'pattern':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'learning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'issue_resolution':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'best_practice':
        return 'bg-orange-100 text-orange-800 border-orange-200'
    }
  }

  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        {/* Search Bar */}
        <div className="relative mb-6">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            placeholder="Search knowledge base... (min 2 characters)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Filter Tabs */}
        <div className="flex flex-wrap gap-2">
          {KNOWLEDGE_TYPES.map((type) => (
            <button
              key={type.id}
              onClick={() => setActiveFilter(type.id)}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                activeFilter === type.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <span className="mr-2">{type.icon}</span>
              {type.label}
            </button>
          ))}
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <p className="text-red-800">Failed to load knowledge base: {error.message}</p>
        </div>
      )}

      {/* Knowledge Entries */}
      {!isLoading && !error && (
        <div className="space-y-4">
          {filteredEntries.length > 0 ? (
            filteredEntries.map((entry: KnowledgeEntry) => (
              <div
                key={entry.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{getTypeIcon(entry.knowledge_type)}</span>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{entry.title}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getTypeColor(entry.knowledge_type)}`}>
                          {entry.knowledge_type.replace('_', ' ')}
                        </span>
                        <span className="text-xs text-gray-500">
                          by {entry.created_by} • {new Date(entry.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Content */}
                <div className="prose prose-sm max-w-none mb-4">
                  <p className="text-gray-700">{entry.content}</p>
                </div>

                {/* Tags */}
                {entry.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-3">
                    {entry.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}

                {/* References */}
                {entry.references && entry.references.length > 0 && (
                  <div className="border-t border-gray-200 pt-3">
                    <p className="text-sm text-gray-600 mb-2">References:</p>
                    <ul className="space-y-1">
                      {entry.references.map((ref, index) => (
                        <li key={index} className="text-sm text-blue-600 hover:underline">
                          <a href={ref} target="_blank" rel="noopener noreferrer">
                            {ref}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Footer */}
                <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-200 text-xs text-gray-500">
                  <span>Updated {new Date(entry.updated_at).toLocaleDateString()}</span>
                  <button className="text-blue-600 hover:text-blue-800 font-medium">
                    View Details →
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
              <div className="text-6xl mb-4">🔍</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {searchQuery || activeFilter !== 'all' ? 'No Results Found' : 'Start Searching'}
              </h3>
              <p className="text-gray-600">
                {searchQuery || activeFilter !== 'all'
                  ? 'Try adjusting your search or filters'
                  : 'Enter a search query to find knowledge entries'}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
