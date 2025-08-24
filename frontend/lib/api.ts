import { 
  LoginRequest, 
  LoginResponse, 
  RegisterRequest, 
  User,
  UploadResponse,
  BankType,
  ImportCommitRequest,
  ImportCommitResponse,
  PLSummaryRequest,
  PLSummaryResponse,
  TransactionListRequest,
  TransactionListResponse
} from '@/types/api.types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private baseURL: string;
  
  constructor() {
    this.baseURL = API_URL;
  }
  
  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token');
    }
    return null;
  }
  
  private setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token);
    }
  }
  
  public clearToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
  }
  
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    
    const headers: HeadersInit = {
      ...options.headers,
    };
    
    // Always add Authorization header if token exists, except for login/register
    const isPublicEndpoint = endpoint === '/api/auth/login' || endpoint === '/api/auth/register';
    if (token && !isPublicEndpoint) {
      headers['Authorization'] = `Bearer ${token}`;
      console.log('Adding auth header with token:', token.substring(0, 20) + '...');
    }
    
    if (options.body && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }
    
    console.log('API Request:', {
      endpoint,
      method: options.method || 'GET',
      hasToken: !!token,
      isPublicEndpoint,
      authHeader: headers['Authorization'] ? 'Present' : 'Missing',
      headers
    });
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers,
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        this.clearToken();
        if (typeof window !== 'undefined' && !endpoint.includes('/auth/')) {
          window.location.href = '/login';
        }
      }
      
      let errorMessage = 'An error occurred';
      try {
        const errorText = await response.text();
        console.error('API Error response text:', errorText);
        
        // Try to parse as JSON
        if (errorText) {
          try {
            const error = JSON.parse(errorText);
            errorMessage = error.detail || error.message || error.error || 
                          (Object.keys(error).length === 0 ? `Request failed (${response.status})` : JSON.stringify(error));
          } catch {
            // Not JSON, use the text directly
            errorMessage = errorText;
          }
        } else {
          errorMessage = `Request failed with status ${response.status}`;
        }
      } catch {
        errorMessage = `Request failed with status ${response.status}`;
      }
      throw new Error(errorMessage);
    }
    
    return response.json();
  }
  
  // Authentication methods
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.request<LoginResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    
    console.log('Login response:', response);
    
    if (response.access_token) {
      this.setToken(response.access_token);
      console.log('Token saved to localStorage');
      // Verify token was saved
      const savedToken = this.getToken();
      console.log('Token retrieved from localStorage:', savedToken ? 'Yes' : 'No');
    }
    
    return response;
  }
  
  async register(data: RegisterRequest): Promise<User> {
    return this.request<User>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
  
  async getCurrentUser(): Promise<User> {
    const token = this.getToken();
    console.log('getCurrentUser - Token exists:', !!token);
    if (!token) {
      throw new Error('No authentication token found');
    }
    return this.request<User>('/api/auth/me');
  }
  
  // Upload methods
  async uploadCSV(
    file: File,
    bank: BankType,
    periodMonth: string
  ): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('bank', bank);
    formData.append('period_month', periodMonth);
    
    console.log('Uploading file:', {
      fileName: file.name,
      fileSize: file.size,
      fileType: file.type,
      bank,
      periodMonth
    });
    
    return this.request<UploadResponse>('/api/upload', {
      method: 'POST',
      body: formData,
    });
  }
  
  async commitImport(data: ImportCommitRequest): Promise<ImportCommitResponse> {
    return this.request<ImportCommitResponse>('/api/import/commit', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
  
  // P&L methods
  async getPLSummary(params: PLSummaryRequest): Promise<PLSummaryResponse> {
    return this.request<PLSummaryResponse>('/api/pl/summary', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }
  
  // Transaction methods
  async getTransactions(params: TransactionListRequest): Promise<TransactionListResponse> {
    return this.request<TransactionListResponse>('/api/tx', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }
}

export const api = new APIClient();