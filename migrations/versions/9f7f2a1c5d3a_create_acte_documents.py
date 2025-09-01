"""create acte_documents table

Revision ID: 9f7f2a1c5d3a
Revises: b82b31517250
Create Date: 2025-08-29 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f7f2a1c5d3a'
down_revision = 'b82b31517250'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'acte_documents',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('acte_id', sa.Integer(), sa.ForeignKey('actes_avocat.acte_id', ondelete='CASCADE'), nullable=False),
        sa.Column('storage_path', sa.String(length=255), nullable=False),
        sa.Column('original_name', sa.String(length=255), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('size_bytes', sa.Integer(), nullable=True),
        sa.Column('sha256_hash', sa.String(length=64), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
    )
    op.create_index('ix_acte_documents_acte_id', 'acte_documents', ['acte_id'])
    op.create_index('ix_acte_documents_uploaded_at', 'acte_documents', ['uploaded_at'])


def downgrade():
    op.drop_index('ix_acte_documents_uploaded_at', table_name='acte_documents')
    op.drop_index('ix_acte_documents_acte_id', table_name='acte_documents')
    op.drop_table('acte_documents')
