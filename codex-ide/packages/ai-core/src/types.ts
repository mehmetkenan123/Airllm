/**
 * Core types for AI functionality in Codex IDE
 */

export interface ModelConfig {
  id: string;
  name: string;
  type: 'airllm' | 'llama-cpp' | 'webllm' | 'openai-compatible';
  path?: string;
  url?: string;
  contextLength: number;
  parameters: number;
  quantization?: 'Q2_K' | 'Q3_K' | 'Q4_K_M' | 'Q5_K_M' | 'Q6_K' | 'Q8_0';
  layers?: number;
  gpuLayers?: number;
  temperature?: number;
  topP?: number;
  maxTokens?: number;
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
  timestamp?: number;
}

export interface InferenceRequest {
  modelId: string;
  messages: ChatMessage[];
  temperature?: number;
  topP?: number;
  maxTokens?: number;
  stream?: boolean;
  stopSequences?: string[];
  context?: CodeContext;
}

export interface CodeContext {
  filePath?: string;
  language?: string;
  code?: string;
  symbols?: SymbolInfo[];
  recentFiles?: string[];
}

export interface SymbolInfo {
  name: string;
  type: 'function' | 'class' | 'variable' | 'import';
  range: { start: number; end: number };
}

export interface InferenceResponse {
  content: string;
  modelId: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  finishReason?: 'stop' | 'length' | 'error';
}

export interface StreamChunk {
  content: string;
  done: boolean;
  modelId?: string;
}

export interface EmbeddingRequest {
  modelId: string;
  text: string;
}

export interface EmbeddingResponse {
  embedding: number[];
  dimensions: number;
}

export interface ModelHealth {
  status: 'healthy' | 'loading' | 'error' | 'unloaded';
  memoryUsage: number;
  loadTime?: number;
  lastUsed?: number;
  error?: string;
}

export interface BackendCapabilities {
  supportsStreaming: boolean;
  supportsEmbeddings: boolean;
  supportsImages: boolean;
  maxContextLength: number;
  availableModels: string[];
}

export type BackendType = 'airllm' | 'llama-cpp' | 'webllm' | 'openai-compatible';

export interface AIBackend {
  type: BackendType;
  initialize(): Promise<void>;
  loadModel(config: ModelConfig): Promise<void>;
  unloadModel(modelId: string): Promise<void>;
  infer(request: InferenceRequest): Promise<InferenceResponse>;
  inferStream(request: InferenceRequest): AsyncGenerator<StreamChunk>;
  getHealth(modelId: string): ModelHealth;
  getCapabilities(): BackendCapabilities;
  dispose(): Promise<void>;
}
