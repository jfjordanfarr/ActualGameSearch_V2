/**
 * ActualGameSearch V2 - Hybrid Search Engine Service
 * TypeScript implementation of Phase 2 hybrid search (FTS5 + Vector Fusion)
 * 
 * Mirrors the Python implementation in phase2_hybrid_search.py
 */

import {
    SearchRequest,
    SearchResponse,
    GameResult,
    LexicalResult,
    SemanticResult,
    FusedResult,
    ScoringSignals,
    FourRScores,
    AutocompleteResponse,
    SimilarGamesRequest,
    SimilarGamesResponse,
    validateWeights,
    validatePagination,
    DEFAULT_VECTOR_K,
    DEFAULT_LEXICAL_K,
    RRF_K_PARAMETER
} from '../models/searchTypes'

import { Env } from '../bindings'
import { D1Service } from './d1Service'
import { VectorizeService } from './vectorizeService'
import { EmbeddingService } from './embedder'
import { RankingService } from './rankingService'

export class HybridSearchEngine {
    private d1Service: D1Service
    private vectorizeService: VectorizeService
    private embeddingService: EmbeddingService
    private rankingService: RankingService

    constructor(private env: Env) {
        this.d1Service = new D1Service(env)
        this.vectorizeService = new VectorizeService(env)
        this.embeddingService = new EmbeddingService(env)
        this.rankingService = new RankingService()
    }

    /**
     * Execute hybrid search pipeline matching Phase 2 Python implementation
     * 
     * Stage 1: FTS5 Lexical Recall (BM25 ranking)
     * Stage 2: Semantic Filtering (vector similarity on candidates)
     * Stage 3: Hybrid Fusion (RRF + 4R scoring)
     */
    async search(request: SearchRequest): Promise<SearchResponse> {
        const startTime = Date.now()

        // Validate and set defaults
        const weights = validateWeights(request.weights || {})
        const pagination = validatePagination(request.page, request.page_size)

        try {
            // Stage 1: FTS5 Lexical Recall
            const lexicalStartTime = Date.now()
            const lexicalResults = await this.d1Service.fts5Search(request.q, request.filters, DEFAULT_LEXICAL_K)
            const lexicalTime = Date.now() - lexicalStartTime

            if (lexicalResults.length === 0) {
                return this.emptyResponse(pagination.page, pagination.page_size, {
                    candidate_count: 0,
                    vector_k: 0,
                    query_time_ms: Date.now() - startTime,
                    stage_times: { lexical_ms: lexicalTime, semantic_ms: 0, fusion_ms: 0 }
                })
            }

            // Stage 2: Semantic Filtering
            const semanticStartTime = Date.now()
            const candidateAppIds = lexicalResults.map((r: LexicalResult) => r.app_id)
            const queryEmbedding = await this.embeddingService.embedQuery(request.q)
            const semanticResults = await this.vectorizeService.similaritySearch(
                queryEmbedding,
                candidateAppIds,
                DEFAULT_VECTOR_K
            )
            const semanticTime = Date.now() - semanticStartTime

            // Stage 3: Hybrid Fusion
            const fusionStartTime = Date.now()
            const fusedResults = this.reciprocalRankFusion(lexicalResults, semanticResults)
            const rankedResults = await this.rankingService.apply4RScoring(fusedResults, weights)
            const finalResults = await this.convertToGameResults(rankedResults)
            const fusionTime = Date.now() - fusionStartTime

            // Apply pagination
            const paginatedResults = this.paginateResults(finalResults, pagination.page, pagination.page_size)

            return {
                results: paginatedResults,
                facets: { tags: {}, platforms: {}, release_years: {}, price_ranges: {} },
                pagination: {
                    page: pagination.page,
                    page_size: pagination.page_size,
                    total_results: finalResults.length,
                    total_pages: Math.ceil(finalResults.length / pagination.page_size)
                },
                debug: {
                    candidate_count: lexicalResults.length,
                    vector_k: semanticResults.length,
                    query_time_ms: Date.now() - startTime,
                    stage_times: {
                        lexical_ms: lexicalTime,
                        semantic_ms: semanticTime,
                        fusion_ms: fusionTime
                    }
                }
            }

        } catch (error) {
            console.error('Search error:', error)
            return this.emptyResponse(pagination.page, pagination.page_size, {
                candidate_count: 0,
                vector_k: 0,
                query_time_ms: Date.now() - startTime,
                stage_times: { lexical_ms: 0, semantic_ms: 0, fusion_ms: 0 },
                error: error instanceof Error ? error.message : 'Unknown error'
            })
        }
    }

    /**
     * Generate autocomplete suggestions
     * Uses multiple strategies for comprehensive suggestions
     */
    async suggest(query: string): Promise<AutocompleteResponse> {
        const startTime = Date.now()

        try {
            // For now, use simple FTS5 search to get game titles
            const searchResults = await this.d1Service.fts5Search(query, undefined, 10)
            const suggestions = searchResults.map(result => ({
                text: result.app_name,
                type: 'title' as const,
                product_id: result.app_id
            }))

            return {
                suggestions: suggestions.slice(0, 10) // Limit to top 10
            }

        } catch (error) {
            // console.error('Autocomplete error:', error)
            return { suggestions: [] }
        }
    }

    /**
     * Find similar games using multiple strategies
     * Future: Will integrate offline-computed relatedness from PACMap/TriMAP
     */
    async findSimilarGames(request: SimilarGamesRequest): Promise<SimilarGamesResponse> {
        const startTime = Date.now()

        try {
            // For now, use the vectorize service to find similar games
            const semanticResults = await this.vectorizeService.findSimilarGames(
                request.product_id,
                request.strategy || 'review_vectors'
            )

            // Convert SemanticResult[] to SimilarGame[]
            const similarGames = await this.convertSemanticResultsToSimilarGames(semanticResults)

            return {
                similar_games: similarGames.slice(0, request.limit || 10),
                strategy_used: request.strategy || 'review_vectors',
                debug: {
                    embedding_count: semanticResults.length,
                    query_time_ms: Date.now() - startTime
                }
            }

        } catch (error) {
            // console.error('Error finding similar games:', error)
            return {
                similar_games: [],
                strategy_used: request.strategy || 'review_vectors',
                debug: {
                    embedding_count: 0,
                    query_time_ms: Date.now() - startTime
                }
            }
        }
    }

    /**
     * Reciprocal Rank Fusion - combines lexical and semantic rankings
     */
    private reciprocalRankFusion(
        lexicalResults: LexicalResult[],
        semanticResults: SemanticResult[]
    ): FusedResult[] {
        const fusedMap = new Map<string, FusedResult>()

        // Add lexical results
        lexicalResults.forEach((result, index) => {
            const key = `${result.app_id}_${result.id}`
            fusedMap.set(key, {
                id: result.id,
                app_id: result.app_id,
                review_text: result.review_text,
                app_name: result.app_name,
                rrf_score: 1 / (RRF_K_PARAMETER + index + 1),
                lexical_rank: index + 1,
                has_lexical: true,
                has_semantic: false
            })
        })

        // Add/merge semantic results
        semanticResults.forEach((result, index) => {
            const key = `${result.app_id}_${result.id}`
            const existing = fusedMap.get(key)

            if (existing) {
                // Merge with existing lexical result
                existing.rrf_score += 1 / (RRF_K_PARAMETER + index + 1)
                existing.semantic_rank = index + 1
                existing.has_semantic = true
            } else {
                // Add new semantic-only result
                fusedMap.set(key, {
                    id: result.id,
                    app_id: result.app_id,
                    review_text: result.review_text,
                    app_name: '', // Will be filled in convertToGameResults
                    rrf_score: 1 / (RRF_K_PARAMETER + index + 1),
                    semantic_rank: index + 1,
                    has_lexical: false,
                    has_semantic: true
                })
            }
        })

        // Convert to array and sort by RRF score
        return Array.from(fusedMap.values())
            .sort((a, b) => b.rrf_score - a.rrf_score)
    }

    /**
     * Convert fused results to final game results with metadata
     */
    private async convertToGameResults(fusedResults: FusedResult[]): Promise<GameResult[]> {
        // Group by app_id to get unique games
        const gameMap = new Map<number, FusedResult[]>()

        for (const result of fusedResults) {
            if (!gameMap.has(result.app_id)) {
                gameMap.set(result.app_id, [])
            }
            gameMap.get(result.app_id)!.push(result)
        }

        // Get app metadata for all unique games
        const appIds = Array.from(gameMap.keys())
        const appMetadata = await this.d1Service.getAppsByIds(appIds)

        // Build final results
        const gameResults: GameResult[] = []

        for (const [appId, results] of gameMap.entries()) {
            const metadata = appMetadata.find((app: any) => app.app_id === appId)
            if (!metadata) continue

            // Use the highest scoring result for this game
            const bestResult = results[0]

            gameResults.push({
                product_id: appId,
                title: metadata.name,
                short_description: metadata.short_description,
                price_final: metadata.price_final,
                is_free: metadata.is_free,
                tags: JSON.parse(metadata.tags_json || '[]'),
                platforms: JSON.parse(metadata.platforms_json || '[]'),
                release_date: metadata.release_date,
                score: bestResult.final_score || bestResult.rrf_score,
                signals: {
                    bm25: bestResult.lexical_rank ? 1.0 / bestResult.lexical_rank : 0,
                    semantic: bestResult.semantic_rank ? 1.0 / bestResult.semantic_rank : 0,
                    rrf: bestResult.rrf_score,
                    four_r: bestResult.four_r_breakdown || {
                        relevance: 0,
                        reputation: 0,
                        recency: 0,
                        repetition: 0
                    }
                }
            })
        }

        return gameResults
    }

    /**
     * Convert SemanticResult[] to SimilarGame[] format
     */
    private async convertSemanticResultsToSimilarGames(semanticResults: SemanticResult[]): Promise<Array<{ product_id: number; title: string; similarity_score: number; shared_tags: string[] }>> {
        // Group by app_id to get unique games
        const gameMap = new Map<number, SemanticResult[]>()

        for (const result of semanticResults) {
            if (!gameMap.has(result.app_id)) {
                gameMap.set(result.app_id, [])
            }
            gameMap.get(result.app_id)!.push(result)
        }

        // Get app metadata for unique games
        const appIds = Array.from(gameMap.keys())
        const appMetadata = await this.d1Service.getAppsByIds(appIds)

        // Build similar games array
        const similarGames = []

        for (const [appId, results] of gameMap.entries()) {
            const metadata = appMetadata.find((app: any) => app.app_id === appId)
            if (!metadata) continue

            // Use highest similarity score for this game
            const bestResult = results[0]

            similarGames.push({
                product_id: appId,
                title: metadata.name,
                similarity_score: bestResult.similarity_score,
                shared_tags: [] // Will be filled by enhanceSimilarGamesWithTags if needed
            })
        }

        return similarGames
    }

    /**
     * Helper methods for autocomplete (removed for now since not all D1 methods exist)
     */
    /**
     * Future implementation placeholders for similar games strategies
     * These will be implemented when we add the offline computation features
     */

    private async enhanceSimilarGamesWithTags(similarGames: Array<{ product_id: number; title: string; similarity_score: number; shared_tags: string[] }>, sourceProductId: number): Promise<Array<{ product_id: number; title: string; similarity_score: number; shared_tags: string[] }>> {
        // Get source game tags
        const sourceMetadata = await this.d1Service.getAppsByIds([sourceProductId])
        if (sourceMetadata.length === 0) return similarGames

        const sourceTags = JSON.parse(sourceMetadata[0].tags_json || '[]')

        // Enhance each similar game with shared tags
        for (const game of similarGames) {
            const gameMetadata = await this.d1Service.getAppsByIds([game.product_id])
            if (gameMetadata.length > 0) {
                const gameTags = JSON.parse(gameMetadata[0].tags_json || '[]')
                game.shared_tags = sourceTags.filter((tag: string) => gameTags.includes(tag))
            }
        }

        return similarGames
    }

    /**
     * Apply pagination to results
     */
    private paginateResults(results: GameResult[], page: number, pageSize: number): GameResult[] {
        const startIndex = (page - 1) * pageSize
        const endIndex = startIndex + pageSize
        return results.slice(startIndex, endIndex)
    }

    /**
     * Return empty response for zero results
     */
    private emptyResponse(page: number, pageSize: number, debug: any): SearchResponse {
        return {
            results: [],
            facets: { tags: {}, platforms: {}, release_years: {}, price_ranges: {} },
            pagination: { page, page_size: pageSize, total_results: 0, total_pages: 0 },
            debug
        }
    }
}
