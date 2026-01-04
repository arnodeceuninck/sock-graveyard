export interface User {
  id: number;
  username: string;
  created_at: string;
}

export interface Sock {
  id: number;
  owner_id: number;
  image_path: string;
  is_matched: boolean;
  created_at: string;
}

export interface SockMatch {
  sock_id: number;
  similarity: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}
