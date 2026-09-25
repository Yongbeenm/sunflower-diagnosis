export interface User {
  id: number;
  email: string;
  username: string;
  role: string;
  permissions: string[];
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginCredentials {
  identifier: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  username: string;
  password: string;
}

export interface UpdateMeCredentials {
  email?: string;
  username?: string;
  new_password?: string;
  current_password: string;
}
