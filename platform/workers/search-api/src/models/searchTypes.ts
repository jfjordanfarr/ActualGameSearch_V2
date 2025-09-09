/**
 * ActualGameSearch V2 - Search API Types & Schemas
 * Based on requirements from actual_game_search_requirements_pack_v_0_1.md
 */

// ===== SEARCH REQUEST/RESPONSE TYPES =====

export interface SearchRequest {
    q: string                           // Search query
    filters?: SearchFilters            // Platform, tags, price, etc.
    weights?: FourRWeights            // 4R scoring weights
    page?: number                     // Page number (1-based)
    page_size?: number               // Results per page (default 20)
}

export interface SearchFilters {
    platform?: string[]              // ["windows", "mac", "linux"]  
    tags?: string[]                  // ["farming", "life-sim"]
    release_year_min?: number        // 2015
    release_year_max?: number        // 2024
    price_min?: number              // 0.00
    price_max?: number              // 30.00
    controller_support?: boolean     // true/false
    languages?: string[]            // ["english", "spanish"]
    is_free?: boolean               // true/false
}

export interface FourRWeights {
    relevance: number    // 0.0 - 1.0 (default 0.55)
    reputation: number   // 0.0 - 1.0 (default 0.20) 
    recency: number     // 0.0 - 1.0 (default 0.15)
    repetition: number  // 0.0 - 1.0 (default 0.10)
}

export interface SearchResponse {
    results: GameResult[]
    facets: SearchFacets
    pagination: PaginationInfo
    debug: DebugInfo
}

export interface GameResult {
    product_id: number
    title: string
    short_description?: string
    price_final?: number
    is_free: boolean
    tags: string[]
    platforms: string[]
    release_date?: string
    score: number                    // Final combined score
    signals: ScoringSignals         // Breakdown of scoring components
}

export interface ScoringSignals {
    bm25: number                    // FTS5/BM25 lexical score
    semantic: number                // Vector similarity score  
    rrf: number                     // Reciprocal Rank Fusion score
    four_r: FourRScores            // 4R component scores
}

export interface FourRScores {
    relevance: number              // Normalized fusion score
    reputation: number             // Review-based quality score
    recency: number               // Time-based recency score
    repetition: number            // Tag/feature repetition score
}

export interface SearchFacets {
    tags: Record<string, number>          // "farming": 124
    platforms: Record<string, number>     // "windows": 645  
    release_years: Record<string, number> // "2020": 89
    price_ranges: Record<string, number>  // "0-10": 234
}

export interface PaginationInfo {
    page: number                   // Current page (1-based)
    page_size: number             // Results per page
    total_results: number         // Total matching results
    total_pages: number           // Total pages available
}

export interface DebugInfo {
    candidate_count: number        // FTS5 candidates found
    vector_k: number              // Semantic search K value
    query_time_ms: number         // Total query execution time
    stage_times: {
        lexical_ms: number          // FTS5 query time
        semantic_ms: number         // Vector query time  
        fusion_ms: number           // RRF + 4R fusion time
    }
}

// ===== AUTOCOMPLETE TYPES =====

export interface AutocompleteResponse {
    suggestions: AutocompleteSuggestion[]
}

export interface AutocompleteSuggestion {
    text: string                   // Suggested query text
    type: 'title' | 'tag' | 'developer'
    product_id?: number           // If suggestion is a specific game
    count?: number                // Number of matching results
}

// ===== SIMILAR GAMES TYPES =====

export interface SimilarGamesRequest {
    product_id: number
    strategy?: 'review_vectors' | 'game_embedding'
    limit?: number                // Default 10
}

export interface SimilarGamesResponse {
    similar_games: SimilarGame[]
    strategy_used: string
    debug: {
        embedding_count: number     // Number of embeddings compared
        query_time_ms: number
    }
}

export interface SimilarGame {
    product_id: number
    title: string
    similarity_score: number      // Cosine similarity (0-1)
    shared_tags: string[]        // Tags in common with source game
}

// ===== DATABASE RECORD TYPES =====

export interface AppRecord {
    app_id: number
    name: string
    short_description?: string
    detailed_description?: string
    release_date?: string
    price_final?: number
    is_free: boolean
    tags_json: string            // JSON array of tag strings
    platforms_json: string      // JSON array of platform strings  
    controller_support: boolean
    reputation_score: number
    review_count: number
    updated_at: string
}

export interface ReviewRecord {
    id: number
    app_id: number
    review_text: string
    quality_score: number
    word_count: number
    voted_up: boolean
    language: string
    created_at: string
}

export interface ReviewEmbeddingRecord {
    id: number
    app_id: number
    review_text: string
    embedding_json: string       // JSON array of 768 floats
    quality_score: number
}

// ===== HYBRID SEARCH INTERNAL TYPES =====

export interface LexicalResult {
    id: number
    app_id: number
    review_text: string
    app_name: string
    bm25_score: number
    rank: number
}

export interface SemanticResult {
    id: number
    app_id: number
    review_text: string
    similarity_score: number
    rank: number
}

export interface FusedResult {
    id: number
    app_id: number
    review_text: string
    app_name: string
    rrf_score: number
    lexical_rank?: number
    semantic_rank?: number
    has_lexical: boolean
    has_semantic: boolean
    final_score?: number
    four_r_breakdown?: FourRScores
}

// ===== CONSTANTS =====

export const DEFAULT_WEIGHTS: FourRWeights = {
    relevance: 0.55,
    reputation: 0.20,
    recency: 0.15,
    repetition: 0.10
}

export const DEFAULT_PAGE_SIZE = 20
export const MAX_PAGE_SIZE = 100
export const DEFAULT_VECTOR_K = 200
export const DEFAULT_LEXICAL_K = 500
export const RRF_K_PARAMETER = 60

// ===== VALIDATION HELPERS =====

export function validateWeights(weights: Partial<FourRWeights>): FourRWeights {
    const validated = { ...DEFAULT_WEIGHTS, ...weights }

    // Ensure all weights are between 0 and 1
    Object.keys(validated).forEach(key => {
        const value = validated[key as keyof FourRWeights]
        if (value < 0 || value > 1) {
            throw new Error(`Weight ${key} must be between 0 and 1, got ${value}`)
        }
    })

    return validated
}

export function validatePagination(page?: number, page_size?: number): { page: number, page_size: number } {
    const validatedPage = Math.max(1, page || 1)
    const validatedPageSize = Math.min(MAX_PAGE_SIZE, Math.max(1, page_size || DEFAULT_PAGE_SIZE))

    return { page: validatedPage, page_size: validatedPageSize }
}
