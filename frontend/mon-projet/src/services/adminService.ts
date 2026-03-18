import type { UserAdmin, Role, UserRoleUpdate } from '../types/User';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class AdminService {
  private getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };
  }

  async getAllUsers(): Promise<UserAdmin[]> {
    const response = await fetch(`${API_BASE_URL}/admin/users`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des utilisateurs');
    }

    return response.json();
  }

  async getAllRoles(): Promise<Role[]> {
    const response = await fetch(`${API_BASE_URL}/admin/roles`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des rôles');
    }

    return response.json();
  }

  async updateUserRole(userId: number, roleUpdate: UserRoleUpdate): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/admin/users/${userId}/role`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(roleUpdate),
    });

    if (!response.ok) {
      throw new Error('Erreur lors de la mise à jour du rôle');
    }

    return response.json();
  }

  async deleteUser(userId: number): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Erreur lors de la suppression de l\'utilisateur');
    }

    return response.json();
  }
}

export const adminService = new AdminService();