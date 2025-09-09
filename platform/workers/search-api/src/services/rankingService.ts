/**
 * ActualGameSearch V2 - Ranking Service
 * Handles 4R scoring (Relevance, Reputation, Recency, Repetition) and normalization
 */

import {
    FusedResult,
    GameResult,
    FourRWeights,
    FourRScores
} from '../models/searchTypes'

export class RankingService {
    /**
     * Apply 4R scoring to fused results
     * Combines relevance (RRF), reputation, recency, and repetition signals
     */
    async apply4RScoring(
        fusedResults: FusedResult[],
        weights: FourRWeights
    ): Promise<FusedResult[]> {
        if (fusedResults.length === 0) {
            return []
        }

        // Calculate individual 4R components
        const relevanceScores = this.calculateRelevanceScores(fusedResults)
        const reputationScores = await this.calculateReputationScores(fusedResults)
        const recencyScores = await this.calculateRecencyScores(fusedResults)
        const repetitionScores = await this.calculateRepetitionScores(fusedResults)

        // Combine weighted scores
        const scoredResults = fusedResults.map((result, index) => {
            const fourRScore =
                weights.relevance * relevanceScores[index] +
                weights.reputation * reputationScores[index] +
                weights.recency * recencyScores[index] +
                weights.repetition * repetitionScores[index]

            return {
                ...result,
                final_score: fourRScore,
                four_r_breakdown: {
                    relevance: relevanceScores[index],
                    reputation: reputationScores[index],
                    recency: recencyScores[index],
                    repetition: repetitionScores[index]
                }
            }
        })

        // Sort by final 4R score
        return scoredResults.sort((a, b) => (b.final_score || 0) - (a.final_score || 0))
    }

    /**
     * Calculate Relevance scores (normalized RRF scores)
     */
    private calculateRelevanceScores(results: FusedResult[]): number[] {
        if (results.length === 0) return []

        const rrfScores = results.map(r => r.rrf_score)
        return this.normalizeScores(rrfScores)
    }

    /**
     * Calculate Reputation scores (based on review quality, game ratings, etc.)
     */
    private async calculateReputationScores(results: FusedResult[]): Promise<number[]> {
        // For MVP, use simple heuristics
        // TODO: Implement more sophisticated reputation calculation

        const reputationScores = results.map(result => {
            let score = 0.5 // Base score

            // Factor in review quality if available
            // This would come from app metadata in a real implementation

            // For now, return normalized random walk around base
            return Math.max(0, Math.min(1, score + (Math.random() - 0.5) * 0.3))
        })

        return reputationScores
    }

    /**
     * Calculate Recency scores (favor newer games/reviews)
     */
    private async calculateRecencyScores(results: FusedResult[]): Promise<number[]> {
        // For MVP, return uniform scores
        // TODO: Implement actual recency calculation based on release dates

        const recencyScores = results.map(() => 0.5) // Neutral recency
        return recencyScores
    }

    /**
     * Calculate Repetition scores (favor games with multiple signal sources)
     */
    private async calculateRepetitionScores(results: FusedResult[]): Promise<number[]> {
        const repetitionScores = results.map(result => {
            let score = 0.0

            // Boost if present in both lexical and semantic results
            if (result.has_lexical && result.has_semantic) {
                score += 0.8
            } else if (result.has_lexical || result.has_semantic) {
                score += 0.4
            }

            // Additional boost for high-quality reviews
            // This could factor in review helpfulness, length, etc.

            return Math.min(1.0, score)
        })

        return repetitionScores
    }

    /**
     * Normalize scores to 0-1 range
     */
    private normalizeScores(scores: number[]): number[] {
        if (scores.length === 0) return []

        const minScore = Math.min(...scores)
        const maxScore = Math.max(...scores)
        const range = maxScore - minScore

        if (range === 0) {
            // All scores are the same
            return scores.map(() => 0.5)
        }

        return scores.map(score => (score - minScore) / range)
    }

    /**
     * Calculate diversity penalty to avoid too many results from same game
     */
    applyDiversityPenalty(results: FusedResult[], maxPerGame: number = 3): FusedResult[] {
        const gameCountMap = new Map<number, number>()
        const diversifiedResults: FusedResult[] = []

        for (const result of results) {
            const currentCount = gameCountMap.get(result.app_id) || 0

            if (currentCount < maxPerGame) {
                diversifiedResults.push(result)
                gameCountMap.set(result.app_id, currentCount + 1)
            }
        }

        return diversifiedResults
    }

    /**
     * Apply quality threshold filtering
     */
    applyQualityThreshold(results: FusedResult[], minScore: number = 0.1): FusedResult[] {
        return results.filter(result => (result.final_score || 0) >= minScore)
    }

    /**
     * Calculate score confidence based on signal availability
     */
    calculateConfidence(result: FusedResult): number {
        let confidence = 0.5 // Base confidence

        // Boost confidence if multiple signals available
        if (result.has_lexical && result.has_semantic) {
            confidence += 0.3
        } else if (result.has_lexical || result.has_semantic) {
            confidence += 0.1
        }

        // Factor in ranking positions
        if (result.lexical_rank && result.lexical_rank <= 10) {
            confidence += 0.1
        }

        if (result.semantic_rank && result.semantic_rank <= 10) {
            confidence += 0.1
        }

        return Math.min(1.0, confidence)
    }
}
