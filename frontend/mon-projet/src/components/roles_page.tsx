
import React, { useState, useEffect } from 'react';
import type { UserAdmin, Role } from '../types/User';
import { adminService } from '../services/adminService';
import './roles_page.css';

const RolePage: React.FC = () => {
  const [users, setUsers] = useState<UserAdmin[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedUser, setSelectedUser] = useState<UserAdmin | null>(null);
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [usersData, rolesData] = await Promise.all([
        adminService.getAllUsers(),
        adminService.getAllRoles()
      ]);
      setUsers(usersData);
      setRoles(rolesData);
      setError(null);
    } catch (err) {
      setError('Erreur lors du chargement des données');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (user: UserAdmin, newRoleId: number) => {
    try {
      await adminService.updateUserRole(user.user_id, { role_id: newRoleId });
      // Recharger les données pour voir les changements
      await loadData();
      setShowRoleModal(false);
      setSelectedUser(null);
    } catch (err) {
      setError('Erreur lors de la mise à jour du rôle');
      console.error(err);
    }
  };

  const handleDeleteUser = async (user: UserAdmin) => {
    try {
      await adminService.deleteUser(user.user_id);
      // Recharger les données pour voir les changements
      await loadData();
      setShowDeleteModal(false);
      setSelectedUser(null);
    } catch (err) {
      setError('Erreur lors de la suppression de l\'utilisateur');
      console.error(err);
    }
  };

  const openRoleModal = (user: UserAdmin) => {
    setSelectedUser(user);
    setShowRoleModal(true);
  };

  const openDeleteModal = (user: UserAdmin) => {
    setSelectedUser(user);
    setShowDeleteModal(true);
  };

  const closeModals = () => {
    setShowRoleModal(false);
    setShowDeleteModal(false);
    setSelectedUser(null);
  };

  if (loading) {
    return <div className="role-page-loading">Chargement...</div>;
  }

  if (error) {
    return <div className="role-page-error">{error}</div>;
  }

  return (
    <div className="role-page">
      <h1 className="role-page-title">Gestion des Utilisateurs</h1>

      <div className="users-table-container">
        <table className="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Pseudo</th>
              <th>Email</th>
              <th>Login</th>
              <th>Rôles</th>
              <th>Date d'inscription</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.user_id}>
                <td>{user.user_id}</td>
                <td>{user.pseudo || 'N/A'}</td>
                <td>{user.email}</td>
                <td>{user.user_login}</td>
                <td>
                  <div className="roles-list">
                    {user.roles.map((role) => (
                      <span key={role.role_id} className={`role-badge role-${role.role_name.toLowerCase()}`}>
                        {role.role_name}
                      </span>
                    ))}
                  </div>
                </td>
                <td>{new Date(user.created_at).toLocaleDateString('fr-FR')}</td>
                <td>
                  <div className="action-buttons">
                    <button
                      className="btn-edit-role"
                      onClick={() => openRoleModal(user)}
                      title="Changer le rôle"
                    >
                      ✏️ Rôle
                    </button>
                    <button
                      className="btn-delete-user"
                      onClick={() => openDeleteModal(user)}
                      title="Supprimer l'utilisateur"
                    >
                      🗑️ Suppr
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal pour changer le rôle */}
      {showRoleModal && selectedUser && (
        <div className="modal-overlay" onClick={closeModals}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Changer le rôle de {selectedUser.pseudo || selectedUser.user_login}</h2>
            <div className="roles-selection">
              {roles.map((role) => (
                <button
                  key={role.role_id}
                  className={`role-option ${selectedUser.roles.some(r => r.role_id === role.role_id) ? 'active' : ''}`}
                  onClick={() => handleRoleChange(selectedUser, role.role_id)}
                >
                  {role.role_name}
                </button>
              ))}
            </div>
            <button className="btn-cancel" onClick={closeModals}>Annuler</button>
          </div>
        </div>
      )}

      {/* Modal de confirmation de suppression */}
      {showDeleteModal && selectedUser && (
        <div className="modal-overlay" onClick={closeModals}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Confirmer la suppression</h2>
            <p>Êtes-vous sûr de vouloir supprimer définitivement l'utilisateur <strong>{selectedUser.pseudo || selectedUser.user_login}</strong> ?</p>
            <p className="warning-text">Cette action est irréversible et supprimera toutes les données associées.</p>
            <div className="modal-buttons">
              <button className="btn-cancel" onClick={closeModals}>Annuler</button>
              <button
                className="btn-confirm-delete"
                onClick={() => handleDeleteUser(selectedUser)}
              >
                Supprimer définitivement
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RolePage;