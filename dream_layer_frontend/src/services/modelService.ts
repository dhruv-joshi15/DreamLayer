export interface CheckpointModel {
  id: string;
  name: string;
  filename: string;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5002";

// Fetch available checkpoint models
export const fetchAvailableModels = async (): Promise<CheckpointModel[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models`);
    if (!response.ok) {
      throw new Error(`Failed to fetch models: ${response.statusText}`);
    }

    const data = await response.json();
    if (data.status === 'success' && Array.isArray(data.models)) {
      return data.models;
    } else {
      throw new Error('Invalid response format when fetching models');
    }
  } catch (error) {
    console.error('Error fetching models:', error);
    throw error;
  }
};

// Interface for random prompt response
export interface RandomPromptResponse {
  status: string;
  message: string;
  type: string;
  prompt: string;
}

// Fetch a random prompt (positive or negative)
export const fetchRandomPrompt = async (type: 'positive' | 'negative'): Promise<string> => {
  try {
    console.log(`Calling fetch-prompt API with type: ${type}`);
    const response = await fetch(`${API_BASE_URL}/api/fetch-prompt?type=${type}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch ${type} prompt: ${response.statusText}`);
    }
    
    const data: RandomPromptResponse = await response.json();
    if (data.status === 'success') {
      return data.prompt;
    } else {
      throw new Error(data.message || `API failed to return ${type} prompt`);
    }
  } catch (error) {
    console.error(`Error fetching ${type} prompt:`, error);
    throw error;
  }
};

// Fetch available upscaler models
export const fetchUpscalerModels = async (): Promise<string[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/upscaler-models`);
    if (!response.ok) {
      throw new Error(`Failed to fetch upscaler models: ${response.statusText}`);
    }

    const data = await response.json();
    return data.models;
  } catch (error) {
    console.error('Error fetching upscaler models:', error);
    throw error;
  }
};

// Add an API-based model using alias and API key
export const addAPIBasedModel = async (alias: string, apiKey: string): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/add-api-key`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        alias,
        'api-key': apiKey,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to add API-based model');
    }

    return true;
  } catch (error) {
    console.error('Error adding API-based model:', error);
    return false;
  }
};
