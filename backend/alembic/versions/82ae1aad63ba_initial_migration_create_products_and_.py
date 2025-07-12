"""Initial migration: create products and bids tables

Revision ID: 82ae1aad63ba
Revises: 
Create Date: 2025-07-12 23:00:11.094033

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82ae1aad63ba'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('condition', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('suggested_price', sa.Float(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('brand', sa.String(length=100), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for products table
    op.create_index('ix_products_id', 'products', ['id'], unique=False)
    op.create_index('ix_products_title', 'products', ['title'], unique=False)
    op.create_index('ix_products_category', 'products', ['category'], unique=False)
    op.create_index('ix_products_brand', 'products', ['brand'], unique=False)
    
    # Create bids table
    op.create_table(
        'bids',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('bid_id', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('is_auto_bid', sa.Boolean(), nullable=True),
        sa.Column('max_auto_bid', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('bid_id')
    )
    
    # Create indexes for bids table
    op.create_index('ix_bids_id', 'bids', ['id'], unique=False)
    op.create_index('ix_bids_bid_id', 'bids', ['bid_id'], unique=False)
    op.create_index('ix_bids_user_id', 'bids', ['user_id'], unique=False)
    op.create_index('ix_bids_product_id', 'bids', ['product_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop bids table and its indexes
    op.drop_index('ix_bids_product_id', table_name='bids')
    op.drop_index('ix_bids_user_id', table_name='bids')
    op.drop_index('ix_bids_bid_id', table_name='bids')
    op.drop_index('ix_bids_id', table_name='bids')
    op.drop_table('bids')
    
    # Drop products table and its indexes
    op.drop_index('ix_products_brand', table_name='products')
    op.drop_index('ix_products_category', table_name='products')
    op.drop_index('ix_products_title', table_name='products')
    op.drop_index('ix_products_id', table_name='products')
    op.drop_table('products')
