/**
 * Cloudflare Workers Runtime Bindings for ActualGameSearch V2
 * Type definitions for D1, Vectorize, R2, and other platform services
 */

// Main Environment Interface
export interface Env {
    // Database
    DB?: D1Database

    // Vector Search
    VECTORIZE?: VectorizeIndex

    // Object Storage
    R2?: R2Bucket

    // Configuration
    ENVIRONMENT: 'development' | 'production'
    PHASE2_DB_PATH?: string

    // Optional: AI/Embedding Services
    AI?: Ai
}

// D1 Database Types
export interface D1Database {
    prepare(sql: string): D1PreparedStatement
    exec(sql: string): Promise<D1ExecResult>
    batch(statements: D1PreparedStatement[]): Promise<D1ExecResult[]>
}

export interface D1PreparedStatement {
    bind(...values: any[]): D1PreparedStatement
    first(): Promise<any>
    all(): Promise<D1Result>
    run(): Promise<D1ExecResult>
}

export interface D1Result {
    results: any[]
    success: boolean
    meta: {
        duration: number
        rows_read: number
        rows_written: number
    }
}

export interface D1ExecResult {
    success: boolean
    error?: string
    meta: {
        duration: number
        rows_read: number
        rows_written: number
    }
}

// Vectorize Types
export interface VectorizeIndex {
    query(vector: number[], options?: VectorizeQueryOptions): Promise<VectorizeMatches>
    insert(vectors: VectorizeVector[]): Promise<VectorizeInsertResult>
    upsert(vectors: VectorizeVector[]): Promise<VectorizeUpsertResult>
    getByIds(ids: string[]): Promise<VectorizeVector[]>
    deleteByIds(ids: string[]): Promise<VectorizeDeleteResult>
}

export interface VectorizeVector {
    id: string
    values: number[]
    metadata?: Record<string, any>
}

export interface VectorizeQueryOptions {
    topK?: number
    filter?: Record<string, any>
    returnValues?: boolean
    returnMetadata?: boolean
}

export interface VectorizeMatches {
    matches: VectorizeMatch[]
    count: number
}

export interface VectorizeMatch {
    id: string
    score: number
    values?: number[]
    metadata?: Record<string, any>
}

export interface VectorizeInsertResult {
    count: number
    ids: string[]
}

export interface VectorizeUpsertResult {
    count: number
    ids: string[]
}

export interface VectorizeDeleteResult {
    count: number
    ids: string[]
}

// R2 Storage Types  
export interface R2Bucket {
    get(key: string, options?: R2GetOptions): Promise<R2Object | null>
    put(key: string, value: string | ArrayBuffer | ReadableStream, options?: R2PutOptions): Promise<R2Object>
    delete(key: string): Promise<void>
    list(options?: R2ListOptions): Promise<R2Objects>
}

export interface R2Object {
    key: string
    size: number
    etag: string
    httpEtag: string
    uploaded: Date
    body: ReadableStream
    arrayBuffer(): Promise<ArrayBuffer>
    text(): Promise<string>
    json(): Promise<any>
}

export interface R2GetOptions {
    range?: { offset: number; length?: number }
    onlyIf?: { etagMatches?: string; etagDoesNotMatch?: string }
}

export interface R2PutOptions {
    httpMetadata?: { contentType?: string; contentEncoding?: string }
    customMetadata?: Record<string, string>
}

export interface R2ListOptions {
    limit?: number
    prefix?: string
    cursor?: string
    delimiter?: string
}

export interface R2Objects {
    objects: R2Object[]
    truncated: boolean
    cursor?: string
}

// Workers AI Types (for embedding generation)
export interface Ai {
    run(model: string, input: any): Promise<any>
}
