import os
import sys
from pathlib import Path

import environ

def ensure_mysql_database_exists():
    project_root = Path(__file__).resolve().parent
    environ.Env.read_env(project_root / '.env')

    database_name = os.getenv('DB_NAME', 'finance_db')
    database_user = os.getenv('DB_USER', 'root')
    database_password = os.getenv('DB_PASSWORD', '')
    database_host = os.getenv('DB_HOST', '127.0.0.1')
    database_port = int(os.getenv('DB_PORT', '3306'))

    try:
        import MySQLdb
    except ImportError:
        return

    conn = MySQLdb.connect(
        host=database_host,
        user=database_user,
        passwd=database_password,
        port=database_port,
        connect_timeout=5,
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{database_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
    finally:
        conn.close()


def main():
    ensure_mysql_database_exists()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
