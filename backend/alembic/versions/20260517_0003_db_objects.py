"""db objects

Revision ID: 20260517_0003
Revises: 20260517_0002
Create Date: 2026-05-17 12:40:00
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260517_0003"
down_revision: Union[str, None] = "20260517_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE detail_logs (
            id SERIAL PRIMARY KEY,
            detail_id INTEGER NULL,
            operation VARCHAR(20) NOT NULL,
            old_quantity INTEGER NULL,
            new_quantity INTEGER NULL,
            old_price NUMERIC NULL,
            new_price NUMERIC NULL,
            changed_at TIMESTAMP NOT NULL DEFAULT now()
        );
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION fn_check_detail_values()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF NEW.quantity < 0 THEN
                RAISE EXCEPTION 'Количество детали не может быть отрицательным';
            END IF;

            IF NEW.price < 0 THEN
                RAISE EXCEPTION 'Цена детали не может быть отрицательной';
            END IF;

            IF NEW.weight IS NOT NULL AND NEW.weight < 0 THEN
                RAISE EXCEPTION 'Вес детали не может быть отрицательным';
            END IF;

            RETURN NEW;
        END;
        $$;
        """
    )

    op.execute(
        """
        CREATE TRIGGER trigger_check_detail_values
        BEFORE INSERT OR UPDATE ON details
        FOR EACH ROW
        EXECUTE FUNCTION fn_check_detail_values();
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION fn_update_detail_updated_at()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$;
        """
    )

    op.execute(
        """
        CREATE TRIGGER trigger_update_detail_updated_at
        BEFORE UPDATE ON details
        FOR EACH ROW
        EXECUTE FUNCTION fn_update_detail_updated_at();
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION fn_log_detail_changes()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF OLD.quantity IS DISTINCT FROM NEW.quantity
               OR OLD.price IS DISTINCT FROM NEW.price THEN
                INSERT INTO detail_logs (
                    detail_id,
                    operation,
                    old_quantity,
                    new_quantity,
                    old_price,
                    new_price,
                    changed_at
                )
                VALUES (
                    NEW.id,
                    'UPDATE',
                    OLD.quantity,
                    NEW.quantity,
                    OLD.price,
                    NEW.price,
                    now()
                );
            END IF;

            RETURN NEW;
        END;
        $$;
        """
    )

    op.execute(
        """
        CREATE TRIGGER trigger_log_detail_changes
        AFTER UPDATE ON details
        FOR EACH ROW
        EXECUTE FUNCTION fn_log_detail_changes();
        """
    )

    op.execute(
        """
        CREATE OR REPLACE VIEW view_details_full AS
        SELECT
            d.id AS detail_id,
            d.name AS detail_name,
            d.article,
            d.material,
            d.weight,
            d.price,
            d.quantity,
            c.name AS category_name,
            s.name AS supplier_name,
            w.name AS warehouse_name,
            d.created_at,
            d.updated_at
        FROM details d
        JOIN categories c ON c.id = d.category_id
        LEFT JOIN suppliers s ON s.id = d.supplier_id
        LEFT JOIN warehouses w ON w.id = d.warehouse_id;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE VIEW view_low_stock_details AS
        SELECT
            d.id AS detail_id,
            d.name AS detail_name,
            d.article,
            d.quantity,
            c.name AS category_name,
            w.name AS warehouse_name
        FROM details d
        JOIN categories c ON c.id = d.category_id
        LEFT JOIN warehouses w ON w.id = d.warehouse_id
        WHERE d.quantity <= 5;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE VIEW view_supplier_details_summary AS
        SELECT
            s.id AS supplier_id,
            s.name AS supplier_name,
            s.email AS supplier_email,
            COUNT(d.id)::integer AS details_count,
            COALESCE(SUM(d.quantity), 0)::integer AS total_quantity,
            COALESCE(SUM(d.price * d.quantity), 0)::numeric AS total_stock_value
        FROM suppliers s
        LEFT JOIN details d ON d.supplier_id = s.id
        GROUP BY s.id, s.name, s.email;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION get_total_details_count()
        RETURNS integer
        LANGUAGE sql
        STABLE
        AS $$
            SELECT COUNT(*)::integer
            FROM details;
        $$;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION calculate_total_stock_value()
        RETURNS numeric
        LANGUAGE sql
        STABLE
        AS $$
            SELECT COALESCE(SUM(price * quantity), 0)::numeric
            FROM details;
        $$;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION get_details_count_by_category(
            p_category_id integer
        )
        RETURNS integer
        LANGUAGE sql
        STABLE
        AS $$
            SELECT COUNT(*)::integer
            FROM details
            WHERE category_id = p_category_id;
        $$;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE PROCEDURE increase_detail_quantity(
            p_detail_id integer,
            p_amount integer
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF p_amount < 0 THEN
                RAISE EXCEPTION 'Количество для увеличения не может быть отрицательным';
            END IF;

            UPDATE details
            SET quantity = quantity + p_amount
            WHERE id = p_detail_id;

            IF NOT FOUND THEN
                RAISE EXCEPTION 'Деталь с id % не найдена', p_detail_id;
            END IF;
        END;
        $$;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE PROCEDURE decrease_detail_quantity(
            p_detail_id integer,
            p_amount integer
        )
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_quantity integer;
        BEGIN
            IF p_amount < 0 THEN
                RAISE EXCEPTION 'Количество для уменьшения не может быть отрицательным';
            END IF;

            SELECT quantity
            INTO v_quantity
            FROM details
            WHERE id = p_detail_id
            FOR UPDATE;

            IF NOT FOUND THEN
                RAISE EXCEPTION 'Деталь с id % не найдена', p_detail_id;
            END IF;

            IF v_quantity - p_amount < 0 THEN
                RAISE EXCEPTION 'Количество детали не может стать отрицательным';
            END IF;

            UPDATE details
            SET quantity = v_quantity - p_amount
            WHERE id = p_detail_id;
        END;
        $$;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE PROCEDURE set_detail_price(
            p_detail_id integer,
            p_price numeric
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF p_price < 0 THEN
                RAISE EXCEPTION 'Цена детали не может быть отрицательной';
            END IF;

            UPDATE details
            SET price = p_price
            WHERE id = p_detail_id;

            IF NOT FOUND THEN
                RAISE EXCEPTION 'Деталь с id % не найдена', p_detail_id;
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trigger_log_detail_changes ON details;")
    op.execute("DROP TRIGGER IF EXISTS trigger_update_detail_updated_at ON details;")
    op.execute("DROP TRIGGER IF EXISTS trigger_check_detail_values ON details;")

    op.execute("DROP FUNCTION IF EXISTS fn_log_detail_changes();")
    op.execute("DROP FUNCTION IF EXISTS fn_update_detail_updated_at();")
    op.execute("DROP FUNCTION IF EXISTS fn_check_detail_values();")

    op.execute("DROP PROCEDURE IF EXISTS set_detail_price(integer, numeric);")
    op.execute("DROP PROCEDURE IF EXISTS decrease_detail_quantity(integer, integer);")
    op.execute("DROP PROCEDURE IF EXISTS increase_detail_quantity(integer, integer);")

    op.execute("DROP FUNCTION IF EXISTS get_details_count_by_category(integer);")
    op.execute("DROP FUNCTION IF EXISTS calculate_total_stock_value();")
    op.execute("DROP FUNCTION IF EXISTS get_total_details_count();")

    op.execute("DROP VIEW IF EXISTS view_supplier_details_summary;")
    op.execute("DROP VIEW IF EXISTS view_low_stock_details;")
    op.execute("DROP VIEW IF EXISTS view_details_full;")

    op.execute("DROP TABLE IF EXISTS detail_logs;")
