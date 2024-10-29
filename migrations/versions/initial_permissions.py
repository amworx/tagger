"""Initial permissions setup

Revision ID: initial_permissions
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

def upgrade():
    # Create initial resources
    resources = [
        ('settings', 'Application settings and configurations'),
        ('user_management', 'User management and permissions'),
        ('database_operations', 'Database backup, restore, and maintenance'),
        ('asset_types', 'Asset type management'),
        ('buildings', 'Building management'),
        ('departments', 'Department management'),
        ('tag_generation', 'Tag generation functionality'),
        ('permission_groups', 'Permission group management'),
    ]
    
    for name, description in resources:
        op.execute(f"""
            INSERT INTO resource (name, description)
            VALUES ('{name}', '{description}')
        """)
    
    # Create default permissions for each resource
    for resource_name, _ in resources:
        for ptype in ['read', 'write', 'delete', 'manage']:
            op.execute(f"""
                INSERT INTO permission (resource_id, permission_type)
                SELECT id, '{ptype}'
                FROM resource
                WHERE name = '{resource_name}'
            """)
    
    # Set up default role permissions
    # Superadmin gets all permissions by default
    op.execute("""
        INSERT INTO role_permission (role, permission_id)
        SELECT 'superadmin', id
        FROM permission
    """)
    
    # Admin gets most permissions except sensitive ones
    op.execute("""
        INSERT INTO role_permission (role, permission_id)
        SELECT 'admin', p.id
        FROM permission p
        JOIN resource r ON p.resource_id = r.id
        WHERE r.name NOT IN ('settings', 'database_operations', 'permission_groups')
        OR (r.name IN ('settings', 'database_operations', 'permission_groups') 
            AND p.permission_type = 'read')
    """)
    
    # Regular users get basic read permissions
    op.execute("""
        INSERT INTO role_permission (role, permission_id)
        SELECT 'user', p.id
        FROM permission p
        JOIN resource r ON p.resource_id = r.id
        WHERE r.name IN ('asset_types', 'buildings', 'departments', 'tag_generation')
        AND p.permission_type = 'read'
    """)

def downgrade():
    # Remove all permissions
    op.execute("DELETE FROM role_permission")
    op.execute("DELETE FROM permission")
    op.execute("DELETE FROM resource") 