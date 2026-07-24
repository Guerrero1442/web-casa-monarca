"""refactor_cuidado_infantil_schema

Revision ID: b830f95068e2
Revises: 359957ca45a1
Create Date: 2026-07-23 21:05:35.536463

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b830f95068e2'
down_revision: Union[str, Sequence[str], None] = '359957ca45a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Operaciones DDL atómicas con op.execute() para eliminar tablas obsoletas
    op.execute("DROP TABLE IF EXISTS participaciones CASCADE;")
    op.execute("DROP TABLE IF EXISTS inscripciones CASCADE;")
    op.execute("DROP TABLE IF EXISTS eventos CASCADE;")

    # 2. Operaciones DDL atómicas con op.execute() para actualizar rol en usuarios preservando administradores
    op.execute("ALTER TABLE usuarios ALTER COLUMN rol SET DEFAULT 'madre';")
    op.execute("UPDATE usuarios SET rol = 'madre' WHERE rol != 'admin';")

    # 3. Crear la nueva tabla de eventos
    op.create_table(
        'eventos',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('titulo', sa.String(), nullable=False),
        sa.Column('descripcion', sa.String(), nullable=True),
        sa.Column('inicio_evento', sa.DateTime(timezone=True), nullable=False),
        sa.Column('fin_evento', sa.DateTime(timezone=True), nullable=False),
        sa.Column('capacidad_maxima', sa.Integer(), nullable=False),
        sa.Column('id_admin', sa.UUID(), nullable=False),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['id_admin'], ['usuarios.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_eventos_id'), 'eventos', ['id'], unique=False)

    # 4. Crear la tabla de menores
    op.create_table(
        'menores',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('madre_id', sa.UUID(), nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('fecha_nacimiento', sa.Date(), nullable=False),
        sa.Column('alergias', sa.Text(), nullable=True),
        sa.Column('requerimientos_medicos', sa.Text(), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['madre_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_menores_id'), 'menores', ['id'], unique=False)

    # 5. Crear la tabla de solicitudes
    op.create_table(
        'solicitudes',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('madre_id', sa.UUID(), nullable=False),
        sa.Column('menor_id', sa.UUID(), nullable=False),
        sa.Column('inicio_requerido', sa.DateTime(timezone=True), nullable=False),
        sa.Column('fin_requerido', sa.DateTime(timezone=True), nullable=False),
        sa.Column('estado', sa.String(), nullable=False),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['madre_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['menor_id'], ['menores.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_solicitudes_id'), 'solicitudes', ['id'], unique=False)

    # 6. Crear la tabla de reservas
    op.create_table(
        'reservas',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('evento_id', sa.UUID(), nullable=False),
        sa.Column('solicitud_id', sa.UUID(), nullable=False),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['evento_id'], ['eventos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['solicitud_id'], ['solicitudes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reservas_id'), 'reservas', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_reservas_id'), table_name='reservas')
    op.drop_table('reservas')
    op.drop_index(op.f('ix_solicitudes_id'), table_name='solicitudes')
    op.drop_table('solicitudes')
    op.drop_index(op.f('ix_menores_id'), table_name='menores')
    op.drop_table('menores')
    op.drop_index(op.f('ix_eventos_id'), table_name='eventos')
    op.drop_table('eventos')
