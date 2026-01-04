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

export interface MatchCreate {
  sock1_id: number;
  sock2_id: number;
}

export interface Match {
  id: number;
  sock1_id: number;
  sock2_id: number;
  matched_at: string;
  sock1: Sock;
  sock2: Sock;
}
