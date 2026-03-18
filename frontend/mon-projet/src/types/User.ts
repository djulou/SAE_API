export interface Role {
  role_id: number;
  role_name: string;
}

export interface UserAdmin {
  user_id: number;
  pseudo?: string;
  email: string;
  user_login: string;
  image?: string;
  birth_year?: string;
  created_at: string;
  roles: Role[];
}

export interface UserRoleUpdate {
  role_id: number;
}