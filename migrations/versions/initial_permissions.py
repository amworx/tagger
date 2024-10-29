"""Initial permissions setup

Revision ID: 001_initial_permissions
Revises: 
Create Date: 2024-10-29 16:40:00.000000
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic
revision = '001_initial_permissions'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create tables first
    op.create_table('resource',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(50), unique=True, nullable=False),
        sa.Column('description', sa.String(200))
    )

    op.create_table('permission',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('resource_id', sa.Integer(), sa.ForeignKey('resource.id'), nullable=False),
        sa.Column('permission_type', sa.Enum('READ', 'WRITE', 'DELETE', 'MANAGE', name='permissiontype'), nullable=False)
    )

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
        for ptype in ['READ', 'WRITE', 'DELETE', 'MANAGE']:
            op.execute(f"""
                INSERT INTO permission (resource_id, permission_type)
                SELECT id, '{ptype}'
                FROM resource
                WHERE name = '{resource_name}'
            """)
    
    # Set up default role permissions
    op.create_table('role_permission',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('permission_id', sa.Integer(), sa.ForeignKey('permission.id'), nullable=False)
    )

    # Superadmin gets all permissions
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
            AND p.permission_type = 'READ')
    """)
    
    # Regular users get basic read permissions
    op.execute("""
        INSERT INTO role_permission (role, permission_id)
        SELECT 'user', p.id
        FROM permission p
        JOIN resource r ON p.resource_id = r.id
        WHERE r.name IN ('asset_types', 'buildings', 'departments', 'tag_generation')
        AND p.permission_type = 'READ'
    """)

def downgrade():
    op.execute("DELETE FROM role_permission")
    op.execute("DELETE FROM permission")
    op.execute("DELETE FROM resource")
    op.drop_table('role_permission')
    op.drop_table('permission')
    op.drop_table('resource')