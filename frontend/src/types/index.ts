export interface User {
    id: number;
    login: string;
    created_at: string;
  }
  

  export interface Token {
    access_token: string;
    refresh_token: string;
    token_type: string;
  }
  

  export interface UserRegister {
    login: string;
    password: string;
  }
  

  export interface UserLogin {
    login: string;
    password: string;
  }
  
 
  export interface FileResponse {
    id: number;
    filename: string;
    original_filename: string;
    file_size: number;
    mime_type: string;
    status: 'uploaded' | 'processing' | 'processed' | 'edited' | 'saved';
    created_at: string;
    processed_at: string | null;
    processed_file_path: string | null;
    session_id: string | null;
  }

  export interface PaginatedFileResponse {
    items: FileResponse[];
    total: number;
    page: number;
    per_page: number;
    total_pages: number;
  }
  

  export interface MessageResponse {
    id: number;
    content: string;
    role: 'user' | 'assistant';
    created_at: string;
  }
  

  export interface ChatResponse {
    id: number;
    user_id: number | null;
    created_at: string;
    messages?: MessageResponse[];
  }

export interface ExternalTipResponse {
  title: string;
  content: string;
  source: string;
  fetched_at: string;
  fallback: boolean;
}