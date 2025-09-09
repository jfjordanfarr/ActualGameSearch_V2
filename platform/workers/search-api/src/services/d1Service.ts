/**
 * ActualGameSearch V2 - D1 Database Service  
 * Handles FTS5 lexical search, filtering, and app metadata retrieval
 */

import {
    SearchFilters,
    LexicalResult,
    AppRecord,
    SearchFacets
} from '../models/searchTypes'
import { Env } from '../bindings'

export class D1Service {
    constructor(private env: Env) { }

    /**
     * Execute FTS5 full-text search with BM25 ranking
     * Mirrors Python lexical_search() method
     */
    async fts5Search(
        query: string,
        filters?: SearchFilters,
        limit: number = 500
    ): Promise<LexicalResult[]> {
        if (!this.env.DB) {
            throw new Error('D1 database not available')
        }

        // Build FTS5 query with filters
        const { sql, params } = this.buildFtsQuery(query, filters, limit)

        const result = await this.env.DB.prepare(sql).bind(...params).all()

        if (!result.success) {
            throw new Error('FTS5 query failed')
        }

        return result.results.map((row: any, index: number) => ({
            id: row.id,
            app_id: row.app_id,
            review_text: row.review_text,
            app_name: row.app_name,
            bm25_score: row.rank || 0,
            rank: index + 1
        }))
    }

    /**
     * Get app metadata by IDs
     */
    async getAppsByIds(appIds: number[]): Promise<AppRecord[]> {
        if (!this.env.DB || appIds.length === 0) {
            return []
        }

        const placeholders = appIds.map(() => '?').join(',')
        const sql = `
      SELECT app_id, name, short_description, detailed_description,
             release_date, price_final, is_free, tags_json, platforms_json,
             controller_support, reputation_score, review_count, updated_at
      FROM apps 
      WHERE app_id IN (${placeholders})
    `

        const result = await this.env.DB.prepare(sql).bind(...appIds).all()

        if (!result.success) {
            throw new Error('App metadata query failed')
        }

        return result.results as AppRecord[]
    }

    /**
     * Generate search facets for filtering UI
     */
    async generateFacets(query: string, filters?: SearchFilters): Promise<SearchFacets> {
        if (!this.env.DB) {
            return { tags: {}, platforms: {}, release_years: {}, price_ranges: {} }
        }

        // For MVP, return basic facets from all apps
        // TODO: Generate facets from search results for better UX

        const facets: SearchFacets = {
            tags: await this.getTagCounts(),
            platforms: await this.getPlatformCounts(),
            release_years: await this.getYearCounts(),
            price_ranges: await this.getPriceCounts()
        }

        return facets
    }

    /**
     * Build FTS5 SQL query with filters
     */
    private buildFtsQuery(
        query: string,
        filters?: SearchFilters,
        limit: number = 500
    ): { sql: string, params: any[] } {
        const params: any[] = []

        // Base FTS5 query with JOIN to get app names
        let sql = `
      SELECT r.id, r.app_id, r.review_text, r.quality_score,
             a.name as app_name, fts.rank
      FROM reviews_fts fts
      JOIN reviews r ON r.id = fts.rowid
      JOIN apps a ON a.app_id = r.app_id
      WHERE reviews_fts MATCH ?
    `
        params.push(query)

        // Add filters
        if (filters) {
            if (filters.platform && filters.platform.length > 0) {
                const platformConditions = filters.platform.map(() => 'a.platforms_json LIKE ?').join(' OR ')
                sql += ` AND (${platformConditions})`
                filters.platform.forEach(platform => params.push(`%"${platform}"%`))
            }

            if (filters.tags && filters.tags.length > 0) {
                const tagConditions = filters.tags.map(() => 'a.tags_json LIKE ?').join(' OR ')
                sql += ` AND (${tagConditions})`
                filters.tags.forEach(tag => params.push(`%"${tag}"%`))
            }

            if (filters.price_min !== undefined) {
                sql += ` AND (a.price_final >= ? OR a.is_free = 1)`
                params.push(filters.price_min)
            }

            if (filters.price_max !== undefined) {
                sql += ` AND (a.price_final <= ? OR a.is_free = 1)`
                params.push(filters.price_max)
            }

            if (filters.release_year_min !== undefined) {
                sql += ` AND strftime('%Y', a.release_date) >= ?`
                params.push(filters.release_year_min.toString())
            }

            if (filters.release_year_max !== undefined) {
                sql += ` AND strftime('%Y', a.release_date) <= ?`
                params.push(filters.release_year_max.toString())
            }

            if (filters.is_free !== undefined) {
                sql += ` AND a.is_free = ?`
                params.push(filters.is_free ? 1 : 0)
            }

            if (filters.controller_support !== undefined) {
                sql += ` AND a.controller_support = ?`
                params.push(filters.controller_support ? 1 : 0)
            }
        }

        // Sort by FTS5 rank and limit
        sql += ` ORDER BY fts.rank LIMIT ?`
        params.push(limit)

        return { sql, params }
    }

    /**
     * Get tag counts for facets
     */
    private async getTagCounts(): Promise<Record<string, number>> {
        if (!this.env.DB) return {}

        // Simple implementation - could be optimized with JSON_EXTRACT in production
        const result = await this.env.DB.prepare(`
      SELECT tags_json, COUNT(*) as count 
      FROM apps 
      WHERE tags_json IS NOT NULL 
      GROUP BY tags_json
    `).all()

        const tagCounts: Record<string, number> = {}

        if (result.success) {
            result.results.forEach((row: any) => {
                try {
                    const tags = JSON.parse(row.tags_json || '[]')
                    tags.forEach((tag: string) => {
                        tagCounts[tag] = (tagCounts[tag] || 0) + (row.count || 1)
                    })
                } catch (e) {
                    // Skip invalid JSON
                }
            })
        }

        return tagCounts
    }

    /**
     * Get platform counts for facets
     */
    private async getPlatformCounts(): Promise<Record<string, number>> {
        if (!this.env.DB) return {}

        const result = await this.env.DB.prepare(`
      SELECT platforms_json, COUNT(*) as count 
      FROM apps 
      WHERE platforms_json IS NOT NULL 
      GROUP BY platforms_json
    `).all()

        const platformCounts: Record<string, number> = {}

        if (result.success) {
            result.results.forEach((row: any) => {
                try {
                    const platforms = JSON.parse(row.platforms_json || '[]')
                    platforms.forEach((platform: string) => {
                        platformCounts[platform] = (platformCounts[platform] || 0) + (row.count || 1)
                    })
                } catch (e) {
                    // Skip invalid JSON
                }
            })
        }

        return platformCounts
    }

    /**
     * Get release year counts for facets
     */
    private async getYearCounts(): Promise<Record<string, number>> {
        if (!this.env.DB) return {}

        const result = await this.env.DB.prepare(`
      SELECT strftime('%Y', release_date) as year, COUNT(*) as count
      FROM apps 
      WHERE release_date IS NOT NULL
      GROUP BY year
      ORDER BY year DESC
    `).all()

        const yearCounts: Record<string, number> = {}

        if (result.success) {
            result.results.forEach((row: any) => {
                if (row.year) {
                    yearCounts[row.year] = row.count || 0
                }
            })
        }

        return yearCounts
    }

    /**
     * Get price range counts for facets
     */
    private async getPriceCounts(): Promise<Record<string, number>> {
        if (!this.env.DB) return {}

        const result = await this.env.DB.prepare(`
      SELECT 
        CASE 
          WHEN is_free = 1 THEN 'Free'
          WHEN price_final <= 5 THEN '$0-5'
          WHEN price_final <= 15 THEN '$5-15'
          WHEN price_final <= 30 THEN '$15-30'
          WHEN price_final <= 60 THEN '$30-60'
          ELSE '$60+'
        END as price_range,
        COUNT(*) as count
      FROM apps
      GROUP BY price_range
    `).all()

        const priceCounts: Record<string, number> = {}

        if (result.success) {
            result.results.forEach((row: any) => {
                priceCounts[row.price_range] = row.count || 0
            })
        }

        return priceCounts
    }
}
