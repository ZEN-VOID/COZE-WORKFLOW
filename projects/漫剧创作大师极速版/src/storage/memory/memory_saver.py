import psycopg
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.base import BaseCheckpointSaver
from typing import Optional, Union
import logging
import time

from config.settings import get_settings

logger = logging.getLogger(__name__)


class MemoryManager:
    """Memory Manager 单例类"""

    _instance: Optional['MemoryManager'] = None
    _checkpointer: Optional[Union[AsyncPostgresSaver, MemorySaver]] = None
    _pool: Optional[AsyncConnectionPool] = None
    _setup_done: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _connect_with_retry(self, db_url: str) -> Optional[psycopg.Connection]:
        """带重试的数据库连接，每次 15 秒超时，共尝试 2 次"""
        checkpoint_settings = get_settings().checkpoint
        last_error = None
        for attempt in range(1, checkpoint_settings.max_retries + 1):
            try:
                logger.info(f"Attempting database connection (attempt {attempt}/{checkpoint_settings.max_retries})")
                conn = psycopg.connect(
                    db_url,
                    autocommit=True,
                    connect_timeout=checkpoint_settings.connection_timeout,
                )
                logger.info(f"Database connection established on attempt {attempt}")
                return conn
            except Exception as e:
                last_error = e
                logger.warning(f"Database connection attempt {attempt} failed: {e}")
                if attempt < checkpoint_settings.max_retries:
                    time.sleep(1)
        logger.error(
            f"All {checkpoint_settings.max_retries} database connection attempts failed, last error: {last_error}"
        )
        return None

    def _setup_schema_and_tables(self, db_url: str) -> bool:
        """同步创建 schema 和表（只执行一次），返回是否成功"""
        if self._setup_done:
            return True

        checkpoint_settings = get_settings().checkpoint
        conn = self._connect_with_retry(db_url)
        if conn is None:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute(f"CREATE SCHEMA IF NOT EXISTS {checkpoint_settings.schema_name}")
            conn.execute(f"SET search_path TO {checkpoint_settings.schema_name}")
            PostgresSaver(conn).setup()
            self._setup_done = True
            logger.info("Memory schema and tables created")
            return True
        except Exception as e:
            logger.warning(f"Failed to setup schema/tables: {e}")
            return False
        finally:
            conn.close()

    def _get_db_url_safe(self) -> Optional[str]:
        """安全获取 db_url，失败时返回 None"""
        try:
            from storage.database.db import get_db_url
            db_url = get_db_url()
            if db_url and db_url.strip():
                return db_url
            logger.warning("db_url is empty, will fallback to MemorySaver")
            return None
        except Exception as e:
            logger.warning(f"Failed to get db_url: {e}, will fallback to MemorySaver")
            return None

    def _create_fallback_checkpointer(self) -> MemorySaver:
        """创建内存兜底 checkpointer"""
        self._checkpointer = MemorySaver()
        logger.warning("Using MemorySaver as fallback checkpointer (data will not persist across restarts)")
        return self._checkpointer

    def get_checkpointer(self) -> BaseCheckpointSaver:
        """获取 checkpointer，优先使用 PostgresSaver，失败时退化为 MemorySaver"""
        if self._checkpointer is not None:
            return self._checkpointer

        checkpoint_settings = get_settings().checkpoint
        if checkpoint_settings.backend == "memory":
            return self._create_fallback_checkpointer()

        db_url = self._get_db_url_safe()
        if not db_url:
            return self._create_fallback_checkpointer()

        if not self._setup_schema_and_tables(db_url):
            return self._create_fallback_checkpointer()

        if "?" in db_url:
            db_url = f"{db_url}&options=-csearch_path%3D{checkpoint_settings.schema_name}"
        else:
            db_url = f"{db_url}?options=-csearch_path%3D{checkpoint_settings.schema_name}"

        try:
            self._pool = AsyncConnectionPool(
                conninfo=db_url,
                timeout=checkpoint_settings.connection_timeout,
                min_size=1,
                max_idle=300,
                check=AsyncConnectionPool.check_connection,
            )
            self._checkpointer = AsyncPostgresSaver(self._pool)
            logger.info("AsyncPostgresSaver initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to create AsyncPostgresSaver: {e}, will fallback to MemorySaver")
            return self._create_fallback_checkpointer()

        return self._checkpointer

_memory_manager: Optional[MemoryManager] = None


def get_memory_saver() -> BaseCheckpointSaver:
    """获取 checkpointer，优先使用 PostgresSaver，db_url 不可用或连接失败时退化为 MemorySaver"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager.get_checkpointer()
