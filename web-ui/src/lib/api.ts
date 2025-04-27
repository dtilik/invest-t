// API client for the trading bot
const API_URL = 'http://localhost:8000';

export interface Account {
  id: string;
  name: string;
  type: string;
  status: string;
  opened_date?: string;
}

export interface ApiResponse {
  status?: string;
  message?: string;
  account_id?: string;
  accounts?: Account[];
}

// List all accounts
export async function listAccounts(): Promise<Account[]> {
  try {
    const response = await fetch(`${API_URL}/accounts`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    const data = await response.json() as ApiResponse;
    return data.accounts || [];
  } catch (error) {
    console.error('Failed to fetch accounts:', error);
    return [];
  }
}

// Create a new account
export async function createAccount(): Promise<ApiResponse> {
  try {
    const response = await fetch(`${API_URL}/accounts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json() as ApiResponse;
  } catch (error) {
    console.error('Failed to create account:', error);
    return { status: 'error', message: 'Failed to create account' };
  }
}
