/**
 * ActualGameSearch V2 - Vectorize Service
 * Handles semantic search using Cloudflare Vectorize
 */

import { SemanticResult } from '../models/searchTypes'
import { Env } from '../bindings'

export class VectorizeService {
    constructor(private env: Env) { }

    /**
     * Perform semantic similarity search on filtered candidate IDs
     * Mirrors Python semantic_search() method
     */
    async similaritySearch(
        queryEmbedding: number[],
        candidateIds: number[],
        limit: number = 200
    ): Promise<SemanticResult[]> {
        if (!this.env.VECTORIZE) {
            console.warn('Vectorize not available, falling back to empty semantic results')
            return []
        }

        if (candidateIds.length === 0 || queryEmbedding.length === 0) {
            return []
        }

        try {
            // Query Vectorize with metadata filter for candidate IDs
            const vectorizeResult = await this.env.VECTORIZE.query(queryEmbedding, {
                topK: Math.min(limit, candidateIds.length),
                filter: {
                    review_id: { $in: candidateIds }
                },
                returnValues: false,
                returnMetadata: true
            })

            return vectorizeResult.matches.map((match, index) => ({
                id: parseInt(match.metadata?.review_id?.toString() || '0'),
                app_id: parseInt(match.metadata?.app_id?.toString() || '0'),
                review_text: match.metadata?.review_text?.toString() || '',
                similarity_score: match.score,
                rank: index + 1
            }))

        } catch (error) {
            console.error('Vectorize query failed:', error)
            // Graceful degradation - return empty results
            return []
        }
    }

    /**
     * Find similar games by product ID using review embeddings
     */
    async findSimilarGames(
        productId: number,
        strategy: 'review_vectors' | 'game_embedding' = 'review_vectors',
        limit: number = 10
    ): Promise<SemanticResult[]> {
        if (!this.env.VECTORIZE) {
            return []
        }

        try {
            if (strategy === 'review_vectors') {
                // Get embeddings for this game's reviews and average them
                const gameEmbedding = await this.getAverageGameEmbedding(productId)
                if (!gameEmbedding) return []

                // Find similar games
                const vectorizeResult = await this.env.VECTORIZE.query(gameEmbedding, {
                    topK: limit * 3, // Get more results to filter out same game
                    filter: {
                        app_id: { $ne: productId } // Exclude the source game
                    },
                    returnValues: false,
                    returnMetadata: true
                })

                // Group by app_id and take highest score per game
                const gameScores = new Map<number, SemanticResult>()

                vectorizeResult.matches.forEach((match, index) => {
                    const appId = parseInt(match.metadata?.app_id?.toString() || '0')
                    if (appId && appId !== productId) {
                        const existing = gameScores.get(appId)
                        if (!existing || match.score > existing.similarity_score) {
                            gameScores.set(appId, {
                                id: parseInt(match.metadata?.review_id?.toString() || '0'),
                                app_id: appId,
                                review_text: match.metadata?.review_text?.toString() || '',
                                similarity_score: match.score,
                                rank: index + 1
                            })
                        }
                    }
                })

                return Array.from(gameScores.values())
                    .sort((a, b) => b.similarity_score - a.similarity_score)
                    .slice(0, limit)

            } else {
                // game_embedding strategy - use single embedding per game (if available)
                // TODO: Implement when game-level embeddings are added
                console.warn('game_embedding strategy not yet implemented')
                return []
            }

        } catch (error) {
            console.error('Similar games query failed:', error)
            return []
        }
    }

    /**
     * Get average embedding for a game from its review embeddings
     */
    private async getAverageGameEmbedding(productId: number): Promise<number[] | null> {
        if (!this.env.VECTORIZE) return null

        try {
            // Get all embeddings for this game
            const vectorizeResult = await this.env.VECTORIZE.query([0], { // Dummy query vector
                topK: 200, // Get up to 200 reviews for this game
                filter: {
                    app_id: productId
                },
                returnValues: true,
                returnMetadata: false
            })

            if (vectorizeResult.matches.length === 0) {
                return null
            }

            // Calculate average embedding
            const embeddingDim = vectorizeResult.matches[0].values?.length || 0
            if (embeddingDim === 0) return null

            const averageEmbedding = new Array(embeddingDim).fill(0)

            vectorizeResult.matches.forEach(match => {
                if (match.values) {
                    match.values.forEach((value, i) => {
                        averageEmbedding[i] += value
                    })
                }
            })

            // Normalize by count
            const count = vectorizeResult.matches.length
            return averageEmbedding.map(sum => sum / count)

        } catch (error) {
            console.error('Failed to get average game embedding:', error)
            return null
        }
    }

    /**
     * Health check for Vectorize availability
     */
    async healthCheck(): Promise<boolean> {
        if (!this.env.VECTORIZE) {
            return false
        }

        try {
            // Try a minimal query to test connectivity
            await this.env.VECTORIZE.query([0.1, 0.1], { topK: 1 })
            return true
        } catch {
            return false
        }
    }
}
