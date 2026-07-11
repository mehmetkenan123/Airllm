/**
 * AI Engine - Main orchestration layer for AI functionality
 * Manages backend selection, model routing, and request handling
 */

import type {
  AIBackend,
  BackendType,
  InferenceRequest,
  InferenceResponse,
  StreamChunk,
  ModelConfig,
  ModelHealth,
  BackendCapabilities,
} from './types.js';
import { ContextManager } from './context-manager.js';
import { PromptBuilder } from './prompt-builder.js';
import { StreamingHandler } from './streaming-handler.js';
import { FallbackChain } from './fallback-chain.js';
import { CacheLayer } from './cache-layer.js';
import { PrivacyFilter } from './privacy-filter.js';
import { ModelRouter } from './model-router.js';

export class AIEngine {
  private backends: Map<BackendType, AIBackend> = new Map();
  private contextManager: ContextManager;
  private promptBuilder: PromptBuilder;
  private fallbackChain: FallbackChain;
  private cacheLayer: CacheLayer;
  private privacyFilter: PrivacyFilter;
  private modelRouter: ModelRouter;
  private initialized = false;

  constructor() {
    this.contextManager = new ContextManager();
    this.promptBuilder = new PromptBuilder();
    this.fallbackChain = new FallbackChain();
    this.cacheLayer = new CacheLayer({ maxSize: 1000, ttlMs: 30 * 60 * 1000 });
    this.privacyFilter = new PrivacyFilter();
    this.modelRouter = new ModelRouter();
  }

  /**
   * Register an AI backend
   */
  registerBackend(backend: AIBackend): void {
    this.backends.set(backend.type, backend);
    console.log(`[AIEngine] Registered backend: ${backend.type}`);
  }

  /**
   * Initialize all registered backends
   */
  async initialize(): Promise<void> {
    if (this.initialized) {
      return;
    }

    const initPromises = Array.from(this.backends.values()).map((backend) =>
      backend.initialize().catch((err) => {
        console.error(`[AIEngine] Failed to initialize ${backend.type}:`, err);
        return null;
      })
    );

    await Promise.all(initPromises);
    this.initialized = true;
    console.log('[AIEngine] Initialization complete');
  }

  /**
   * Load a model on the specified backend
   */
  async loadModel(config: ModelConfig): Promise<void> {
    const backend = this.backends.get(config.type);
    if (!backend) {
      throw new Error(`Backend ${config.type} not found`);
    }

    await backend.loadModel(config);
    console.log(`[AIEngine] Loaded model ${config.name} on ${config.type}`);
  }

  /**
   * Perform inference with automatic fallback
   */
  async infer(request: InferenceRequest): Promise<InferenceResponse> {
    // Check cache first
    const cacheKey = this.generateCacheKey(request);
    const cached = await this.cacheLayer.get(cacheKey);
    if (cached) {
      console.log('[AIEngine] Cache hit');
      return cached;
    }

    // Apply privacy filter
    const filteredRequest = await this.privacyFilter.filter(request);

    // Build prompt with context
    const enrichedRequest = await this.enrichRequest(filteredRequest);

    // Route to appropriate model
    const targetModel = this.modelRouter.route(enrichedRequest);

    // Execute with fallback chain
    const response = await this.executeWithFallback({
      ...enrichedRequest,
      modelId: targetModel,
    });

    // Cache response
    await this.cacheLayer.set(cacheKey, response);

    return response;
  }

  /**
   * Stream inference results
   */
  async *inferStream(request: InferenceRequest): AsyncGenerator<StreamChunk> {
    const filteredRequest = await this.privacyFilter.filter(request);
    const enrichedRequest = await this.enrichRequest(filteredRequest);
    const targetModel = this.modelRouter.route(enrichedRequest);

    const handler = new StreamingHandler();

    try {
      const backend = this.getBackendForModel(targetModel);
      if (!backend) {
        throw new Error(`No backend available for model ${targetModel}`);
      }

      const stream = backend.inferStream({
        ...enrichedRequest,
        modelId: targetModel,
      });

      for await (const chunk of stream) {
        const processedChunk = await handler.process(chunk);
        yield processedChunk;
      }
    } catch (error) {
      console.error('[AIEngine] Streaming error:', error);
      yield {
        content: `Error during streaming: ${error instanceof Error ? error.message : 'Unknown error'}`,
        done: true,
      };
    }
  }

  /**
   * Get health status for a model
   */
  getModelHealth(modelId: string): ModelHealth | null {
    for (const backend of this.backends.values()) {
      try {
        const health = backend.getHealth(modelId);
        if (health.status !== 'unloaded') {
          return health;
        }
      } catch {
        // Continue to next backend
      }
    }
    return null;
  }

  /**
   * Get capabilities across all backends
   */
  getCapabilities(): BackendCapabilities {
    const capabilities: BackendCapabilities = {
      supportsStreaming: false,
      supportsEmbeddings: false,
      supportsImages: false,
      maxContextLength: 0,
      availableModels: [],
    };

    for (const backend of this.backends.values()) {
      try {
        const backendCaps = backend.getCapabilities();
        capabilities.supportsStreaming ||= backendCaps.supportsStreaming;
        capabilities.supportsEmbeddings ||= backendCaps.supportsEmbeddings;
        capabilities.supportsImages ||= backendCaps.supportsImages;
        capabilities.maxContextLength = Math.max(
          capabilities.maxContextLength,
          backendCaps.maxContextLength
        );
        capabilities.availableModels.push(...backendCaps.availableModels);
      } catch {
        // Continue to next backend
      }
    }

    return capabilities;
  }

  /**
   * Unload a model
   */
  async unloadModel(modelId: string): Promise<void> {
    for (const backend of this.backends.values()) {
      try {
        await backend.unloadModel(modelId);
        console.log(`[AIEngine] Unloaded model ${modelId}`);
        return;
      } catch {
        // Continue to next backend
      }
    }
    throw new Error(`Model ${modelId} not found on any backend`);
  }

  /**
   * Dispose of all resources
   */
  async dispose(): Promise<void> {
    const disposePromises = Array.from(this.backends.values()).map((backend) =>
      backend.dispose().catch((err) => {
        console.error(`[AIEngine] Error disposing ${backend.type}:`, err);
        return null;
      })
    );

    await Promise.all(disposePromises);
    this.backends.clear();
    this.initialized = false;
    console.log('[AIEngine] Disposed');
  }

  private generateCacheKey(request: InferenceRequest): string {
    const hash = require('crypto').createHash('sha256');
    hash.update(JSON.stringify(request));
    return hash.digest('hex');
  }

  private async enrichRequest(
    request: InferenceRequest
  ): Promise<InferenceRequest> {
    if (request.context) {
      const context = await this.contextManager.buildContext(request.context);
      const prompt = this.promptBuilder.build(request.messages, context);
      return {
        ...request,
        messages: prompt,
      };
    }
    return request;
  }

  private async executeWithFallback(
    request: InferenceRequest
  ): Promise<InferenceResponse> {
    const backends = this.fallbackChain.getFallbackOrder();

    for (const backendType of backends) {
      const backend = this.backends.get(backendType);
      if (!backend) continue;

      try {
        const response = await backend.infer(request);
        return response;
      } catch (error) {
        console.warn(
          `[AIEngine] ${backendType} failed, trying next:`,
          error instanceof Error ? error.message : error
        );
        // Continue to next backend
      }
    }

    throw new Error('All backends failed');
  }

  private getBackendForModel(modelId: string): AIBackend | null {
    for (const backend of this.backends.values()) {
      try {
        const health = backend.getHealth(modelId);
        if (health.status === 'healthy') {
          return backend;
        }
      } catch {
        // Continue to next backend
      }
    }
    return null;
  }
}

// Singleton instance
export const aiEngine = new AIEngine();
