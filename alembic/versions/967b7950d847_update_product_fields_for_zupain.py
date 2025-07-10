"""update product fields for zupain

Revision ID: 967b7950d847
Revises: cc1ca57d788b
Create Date: 2025-07-09 12:59:00.768446

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '967b7950d847'
down_revision: Union[str, Sequence[str], None] = 'cc1ca57d788b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Drop the foreign key constraint on update_logs.product_id
    op.drop_constraint('update_logs_product_id_fkey', 'update_logs', type_='foreignkey')

    # 2. Alter the type of update_logs.product_id to String
    op.alter_column('update_logs', 'product_id',
        existing_type=sa.INTEGER(),
        type_=sa.String(),
        existing_nullable=True
    )

    # 3. Alter the type of products.id to String
    op.alter_column('products', 'id',
        existing_type=sa.INTEGER(),
        type_=sa.String(),
        existing_nullable=False,
        existing_server_default=sa.text("nextval('products_id_seq'::regclass)")
    )

    # 4. Re-create the foreign key constraint
    op.create_foreign_key(
        'update_logs_product_id_fkey',
        'update_logs', 'products',
        ['product_id'], ['id']
    )

    # 5. Continue with your other changes
    op.add_column('products', sa.Column('url', sa.String(), nullable=True))
    op.add_column('products', sa.Column('old_price', sa.String(), nullable=True))
    op.add_column('products', sa.Column('variant', sa.String(), nullable=True))
    op.add_column('products', sa.Column('sizes', sa.JSON(), nullable=True))
    op.add_column('products', sa.Column('main_image', sa.String(), nullable=True))
    op.alter_column('products', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('products', 'price',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               type_=sa.String(),
               nullable=True)
    op.alter_column('products', 'discount',
               existing_type=sa.NUMERIC(precision=5, scale=2),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('products', 'last_updated',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.String(),
               existing_nullable=True)
    op.create_index(op.f('ix_products_url'), 'products', ['url'], unique=True)
    op.drop_constraint(op.f('products_seller_id_fkey'), 'products', type_='foreignkey')
    op.drop_column('products', 'category')
    op.drop_column('products', 'inventory')
    op.drop_column('products', 'seller_id')

def downgrade() -> None:
    # Reverse all changes (for completeness)
    op.add_column('products', sa.Column('seller_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('products', sa.Column('inventory', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('products', sa.Column('category', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.create_foreign_key(op.f('products_seller_id_fkey'), 'products', 'users', ['seller_id'], ['id'])
    op.drop_index(op.f('ix_products_url'), table_name='products')
    op.alter_column('products', 'last_updated',
               existing_type=sa.String(),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('products', 'discount',
               existing_type=sa.String(),
               type_=sa.NUMERIC(precision=5, scale=2),
               existing_nullable=True)
    op.alter_column('products', 'price',
               existing_type=sa.String(),
               type_=sa.NUMERIC(precision=10, scale=2),
               nullable=False)
    op.alter_column('products', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('products', 'id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               existing_server_default=sa.text("nextval('products_id_seq'::regclass)"))
    op.drop_column('products', 'main_image')
    op.drop_column('products', 'sizes')
    op.drop_column('products', 'variant')
    op.drop_column('products', 'old_price')
    op.drop_column('products', 'url')

    # Drop and restore update_logs FK and type
    op.drop_constraint('update_logs_product_id_fkey', 'update_logs', type_='foreignkey')
    op.alter_column('update_logs', 'product_id',
        existing_type=sa.String(),
        type_=sa.INTEGER(),
        existing_nullable=True
    )
    op.create_foreign_key(
        'update_logs_product_id_fkey',
        'update_logs', 'products',
        ['product_id'], ['id']
    )
