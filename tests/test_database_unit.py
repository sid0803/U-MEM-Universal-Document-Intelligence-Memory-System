from app.core.database import get_connection

def test_database_connection():
    conn = get_connection()
    cursor = conn.execute("SELECT 1")
    result = cursor.fetchone()[0]
    conn.close()

    assert result == 1