from __future__ import annotations

import struct
from typing import Any

from azure.identity import DefaultAzureCredential
import pyodbc

from app.config import get_settings

SQL_COPT_SS_ACCESS_TOKEN = 1256
SQL_SCOPE = "https://database.windows.net/.default"


class AzureSqlClient:
    """Generic Azure SQL helper for token-based connectivity."""

    def __init__(self) -> None:
        self._settings = get_settings()

    def _build_connection_string(self) -> str:
        if self._settings.sql_connection_string:
            return self._settings.sql_connection_string

        if not self._settings.sql_server or not self._settings.sql_database:
            raise ValueError(
                "Provide SQL_CONNECTION_STRING or set SQL_SERVER and SQL_DATABASE."
            )

        return (
            "Driver={ODBC Driver 18 for SQL Server};"
            f"Server=tcp:{self._settings.sql_server},{self._settings.sql_port};"
            f"Database={self._settings.sql_database};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
        )

    def _build_access_token_bytes(self) -> bytes:
        credential = DefaultAzureCredential(managed_identity_client_id=self._settings.azure_client_id)
        token = credential.get_token(SQL_SCOPE)
        token_bytes = token.token.encode("utf-16-le")
        return struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)

    def connect(self) -> pyodbc.Connection:
        conn_str = self._build_connection_string()

        if self._settings.sql_connection_string:
            return pyodbc.connect(conn_str)

        token_struct = self._build_access_token_bytes()
        return pyodbc.connect(conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})

    def ping(self) -> bool:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
            return bool(row and row[0] == 1)

    def list_items(
        self,
        table_name: str,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        allowed_tables = {}
        allowed_columns = {}
    
        if table_name not in allowed_tables:
            raise ValueError(f"Invalid table name: {table_name}")
    
        with self.connect() as conn:
            cursor = conn.cursor()
    
            query = f"SELECT TOP (?) * FROM {table_name}"
            params: list[Any] = [limit]
    
            if filters:
                clauses = []
                for key, value in filters.items():
                    if key not in allowed_columns:
                        raise ValueError(f"Invalid filter column: {key}")
                    clauses.append(f"{key} = ?")
                    params.append(value)
    
                query += " WHERE " + " AND ".join(clauses)
    
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
    
        return [dict(zip(columns, row, strict=False)) for row in rows]
