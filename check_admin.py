#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend/app'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Role, UserRole

DATABASE_URL = 'postgresql://user:password@localhost:5433/mabase'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Lister tous les utilisateurs et leurs rôles
    users = db.query(User).all()
    print('Utilisateurs dans la base :')
    for user in users:
        roles = [r.role_name for r in user.roles]
        print(f'ID: {user.user_id}, Login: {user.user_login}, Email: {user.email}, Rôles: {roles}')

    # Vérifier s'il y a un rôle ADMIN
    admin_role = db.query(Role).filter(Role.role_name == 'ADMIN').first()
    if not admin_role:
        print('ERREUR: Le rôle ADMIN n\'existe pas dans la base!')
    else:
        print(f'Rôle ADMIN trouvé (ID: {admin_role.role_id})')

        # Si aucun utilisateur n'a le rôle ADMIN, en donner un à un utilisateur
        admin_users = db.query(User).join(UserRole).join(Role).filter(Role.role_name == 'ADMIN').all()
        if not admin_users:
            print('Aucun utilisateur n\'a le rôle ADMIN. Attribution du rôle ADMIN au premier utilisateur...')
            first_user = db.query(User).first()
            if first_user:
                user_role = UserRole(user_id=first_user.user_id, role_id=admin_role.role_id)
                db.add(user_role)
                db.commit()
                print(f'Rôle ADMIN attribué à {first_user.user_login}')
            else:
                print('Aucun utilisateur trouvé dans la base!')
        else:
            print(f'Utilisateurs avec rôle ADMIN: {[u.user_login for u in admin_users]}')

finally:
    db.close()