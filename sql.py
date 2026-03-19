import sqlite3
import hashlib
import os
from contextlib import contextmanager

# ===================== 核心配置 =====================
DB_NAME = 'schoolnavigation.db'
# 密码加密盐值（随机字符串，可自行修改）
# SALT = os.urandom(16)

FIXED_SALT_HEX = "6d795f746573745f73616c745f313233"  # 对应上面字节串的十六进制
SALT = bytes.fromhex(FIXED_SALT_HEX)

# ===================== 通用工具函数 =====================
@contextmanager
def get_db_connection():
    """
    数据库连接上下文管理器：自动处理连接/关闭/异常
    使用方式：with get_db_connection() as (conn, cur):
    """
    conn = None
    try:
        # 建立连接（check_same_thread=False适配Flask多线程）
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        # 设置行工厂：查询结果可通过列名访问（如row['account']）
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        yield (conn, cur)  # 返回连接和游标
    except sqlite3.Error as e:
        if conn:
            conn.rollback()  # 出错回滚
        raise e  # 抛出异常让上层处理
    finally:
        if conn:
            conn.close()  # 确保连接关闭


def db():
    """
    初始化数据库：创建表（仅首次运行需要）
    新增字段：create_time(创建时间)、update_time(更新时间)
    """
    with get_db_connection() as (conn, cur):
        # 用户表：增加时间字段，优化字段命名（pwd→password）
        create_users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cur.execute(create_users_sql)
        # 可选：创建索引（优化account查询速度）
        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_account ON users(account);")
        conn.commit()
    print("数据库初始化成功！")


# ===================== 密码安全函数 =====================
def encrypt_password(password: str) -> str:
    """
    密码加密：使用SHA256+盐值，防止明文存储
    :param password: 原始密码
    :return: 加密后的密码字符串
    """
    # 拼接盐值后加密
    password_bytes = (password + SALT.hex()).encode('utf-8')
    encrypted = hashlib.sha256(password_bytes).hexdigest()
    return encrypted


# ===================== 业务逻辑函数 =====================
def get_all_users() -> list:
    """查询所有用户（测试/管理用）"""
    with get_db_connection() as (conn, cur):
        cur.execute("SELECT id, account, password ,role, create_time FROM users;")
        # 转换为字典列表（方便前端使用）
        users = [dict(row) for row in cur.fetchall()]
        return users


def verify_user(account: str, password: str) -> bool:
    """
    验证用户登录（替代原db4）
    :param account: 用户名
    :param password: 原始密码
    :return: 是否验证成功
    """
    encrypted_pwd = encrypt_password(password)
    with get_db_connection() as (conn, cur):
        # 使用参数化查询防止SQL注入！！！
        cur.execute(
            "SELECT * FROM users WHERE account = ? AND password = ?",
            (account, encrypted_pwd)  # 参数元组
        )
        user = cur.fetchone()
        return True if user else False


def register_user(account: str, password: str) -> tuple[bool, str]:
    """
    注册用户（替代原db6）
    :param account: 用户名
    :param password: 原始密码
    :return: (是否成功, 提示信息)
    """
    # 先检查用户是否存在（参数化查询）
    with get_db_connection() as (conn, cur):
        cur.execute("SELECT account FROM users WHERE account = ?", (account,))
        if cur.fetchone():
            return False, f"用户名 '{account}' 已存在"

        # 加密密码后插入
        encrypted_pwd = encrypt_password(password)
        try:
            cur.execute(
                "INSERT INTO users (account, password) VALUES (?, ?)",
                (account, encrypted_pwd)
            )
            conn.commit()
            return True, f"用户 '{account}' 注册成功"
        except sqlite3.IntegrityError:
            return False, "注册失败：用户名重复（并发冲突）"
        except Exception as e:
            return False, f"注册失败：{str(e)}"


def update_user_password(account: str, old_pwd: str, new_pwd: str) -> tuple[bool, str]:
    """新增：修改用户密码"""
    # 先验证旧密码
    if not verify_user(account, old_pwd):
        return False, "旧密码错误"

    # 加密新密码并更新
    encrypted_new_pwd = encrypt_password(new_pwd)
    with get_db_connection() as (conn, cur):
        cur.execute(
            "UPDATE users SET password = ?, update_time = CURRENT_TIMESTAMP WHERE account = ?",
            (encrypted_new_pwd, account)
        )
        conn.commit()
        return True, "密码修改成功"


def delete_user(account: str) -> tuple[bool, str]:
    """新增：删除用户"""
    with get_db_connection() as (conn, cur):
        cur.execute("DELETE FROM users WHERE account = ?", (account,))
        if cur.rowcount == 0:
            return False, "用户不存在"
        conn.commit()
        return True, f"用户 '{account}' 删除成功"
#修改用户权限
def create_admin(account, password):
    with get_db_connection() as (conn, cur):
        encrypted_pwd = encrypt_password(password)
        cur.execute("""
            UPDATE users SET role = 'admin' WHERE account = ?
        """, (account,))
        conn.commit()

# ===================== 测试入口 =====================
if __name__ == '__main__':
    # 初始化数据库（首次运行执行）
    # db()
    # 测试注册
    # print(register_user("test123", "Test@123456"))
    # 测试登录验证
    # # print(verify_user("test123", "Test@123456"))
    # 测试查询所有用户
    print(get_all_users())
    # create_admin('1234','Aa123456/')