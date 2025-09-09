/**
 * ActualGameSearch V2 - Cloudflare Worker Entry Point
 * Main API routing and request handling
 */

import { HybridSearchEngine } from './services/searchEngine'
import { Env } from './bindings'
import {
    SearchRequest,
    SearchResponse,
    AutocompleteResponse,
    SimilarGamesRequest,
    SimilarGamesResponse,
    DEFAULT_WEIGHTS,
    validateWeights,
    validatePagination
} from './models/searchTypes'

export default {
    async fetch(request: Request, env: Env, ctx: any): Promise<Response> {
        // CORS headers for all responses
        const corsHeaders = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }

        // Handle CORS preflight
        if (request.method === 'OPTIONS') {
            return new Response(null, { headers: corsHeaders })
        }

        try {
            const url = new URL(request.url)
            const path = url.pathname

            // Initialize search engine
            const searchEngine = new HybridSearchEngine(env)

            // Route handlers
            switch (path) {
                case '/search':
                    return await handleSearch(request, searchEngine, corsHeaders)

                case '/suggest':
                    return await handleAutocomplete(request, searchEngine, corsHeaders)

                case '/similar':
                    return await handleSimilarGames(request, searchEngine, corsHeaders)

                case '/health':
                    return handleHealthCheck(corsHeaders)

                default:
                    return new Response('Not Found', {
                        status: 404,
                        headers: corsHeaders
                    })
            }
        } catch (error) {
            console.error('API Error:', error)
            return new Response(
                JSON.stringify({
                    error: 'Internal server error',
                    message: error instanceof Error ? error.message : 'Unknown error'
                }),
                {
                    status: 500,
                    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
                }
            )
        }
    }
}

/**
 * Handle /search endpoint
 */
async function handleSearch(
    request: Request,
    searchEngine: HybridSearchEngine,
    corsHeaders: Record<string, string>
): Promise<Response> {
    const url = new URL(request.url)

    // Extract search parameters
    const query = url.searchParams.get('q')
    if (!query) {
        return new Response(
            JSON.stringify({ error: 'Missing required parameter: q' }),
            { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        )
    }

    // Parse search request
    const searchRequest: SearchRequest = {
        q: query,
        page: parseInt(url.searchParams.get('page') || '1'),
        page_size: parseInt(url.searchParams.get('page_size') || '20'),
        weights: {
            relevance: parseFloat(url.searchParams.get('weight_relevance') || '0.55'),
            reputation: parseFloat(url.searchParams.get('weight_reputation') || '0.20'),
            recency: parseFloat(url.searchParams.get('weight_recency') || '0.15'),
            repetition: parseFloat(url.searchParams.get('weight_repetition') || '0.10')
        }
    }

    // Validate inputs
    const weights = validateWeights(searchRequest.weights || {})
    const pagination = validatePagination(searchRequest.page, searchRequest.page_size)

    // Execute search
    const startTime = Date.now()
    const searchResponse = await searchEngine.search({
        q: searchRequest.q,
        weights,
        page: pagination.page,
        page_size: pagination.page_size
    })
    const totalTime = Date.now() - startTime

    // Add timing information
    searchResponse.debug.query_time_ms = totalTime

    return new Response(
        JSON.stringify(searchResponse),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
}

/**
 * Handle /suggest endpoint (autocomplete)
 */
async function handleAutocomplete(
    request: Request,
    searchEngine: HybridSearchEngine,
    corsHeaders: Record<string, string>
): Promise<Response> {
    const url = new URL(request.url)
    const query = url.searchParams.get('q')

    if (!query) {
        return new Response(
            JSON.stringify({ error: 'Missing required parameter: q' }),
            { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        )
    }

    const suggestions = await searchEngine.suggest(query)

    return new Response(
        JSON.stringify(suggestions),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
}

/**
 * Handle /similar endpoint
 */
async function handleSimilarGames(
    request: Request,
    searchEngine: HybridSearchEngine,
    corsHeaders: Record<string, string>
): Promise<Response> {
    const url = new URL(request.url)
    const productId = url.searchParams.get('product_id')

    if (!productId) {
        return new Response(
            JSON.stringify({ error: 'Missing required parameter: product_id' }),
            { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        )
    }

    const similarRequest: SimilarGamesRequest = {
        product_id: parseInt(productId),
        strategy: (url.searchParams.get('strategy') as any) || 'review_vectors',
        limit: parseInt(url.searchParams.get('limit') || '10')
    }

    const similarGames = await searchEngine.findSimilarGames(similarRequest)

    return new Response(
        JSON.stringify(similarGames),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
}

/**
 * Handle /health endpoint
 */
function handleHealthCheck(corsHeaders: Record<string, string>): Response {
    const health = {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '2.0.0'
    }

    return new Response(
        JSON.stringify(health),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
}
