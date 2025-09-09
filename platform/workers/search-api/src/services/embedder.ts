/**
 * ActualGameSearch V2 - Embedding Service
 * Handles query embedding generation using Workers AI or external services
 */

import { Env } from '../bindings'

export class EmbeddingService {
    constructor(private env: Env) { }

    /**
     * Generate embedding for search query
     * Uses Workers AI or falls back to external service
     */
    async embedQuery(text: string): Promise<number[]> {
        // Try Workers AI first (if available)
        if (this.env.AI) {
            try {
                const result = await this.env.AI.run('@cf/baai/bge-base-en-v1.5', {
                    text: [text]
                })

                if (result?.data?.[0]) {
                    return result.data[0]
                }
            } catch (error) {
                console.warn('Workers AI embedding failed, falling back:', error)
            }
        }

        // Fallback: Use external embedding service
        return await this.embedWithExternalService(text)
    }

    /**
     * Fallback embedding using external service (e.g., Ollama, OpenAI)
     * For development, this could connect to local Ollama instance
     */
    private async embedWithExternalService(text: string): Promise<number[]> {
        // For development: Try local Ollama (same as Phase 2)
        if (this.env.ENVIRONMENT === 'development') {
            try {
                const response = await fetch('http://127.0.0.1:11434/api/embeddings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        model: 'nomic-embed-text:v1.5',
                        prompt: text
                    })
                })

                if (response.ok) {
                    const result = await response.json()
                    return result.embedding || []
                }
            } catch (error) {
                console.warn('Ollama embedding failed:', error)
            }
        }

        // Production fallback: Could use OpenAI, Cohere, etc.
        // For now, return empty array to gracefully degrade to lexical-only search
        console.warn('No embedding service available, falling back to lexical-only search')
        return []
    }

    /**
     * Batch embed multiple texts (for ETL)
     */
    async embedBatch(texts: string[]): Promise<number[][]> {
        const embeddings: number[][] = []

        // For now, embed one by one
        // TODO: Optimize with true batch processing
        for (const text of texts) {
            const embedding = await this.embedQuery(text)
            embeddings.push(embedding)
        }

        return embeddings
    }

    /**
     * Health check for embedding service
     */
    async healthCheck(): Promise<boolean> {
        try {
            const testEmbedding = await this.embedQuery('test')
            return testEmbedding.length > 0
        } catch {
            return false
        }
    }

    /**
     * Get embedding dimension
     */
    async getEmbeddingDimension(): Promise<number> {
        try {
            const testEmbedding = await this.embedQuery('test')
            return testEmbedding.length
        } catch {
            return 0
        }
    }
}
