import sqlite3
def db():
    #建库
    conn = sqlite3.connect('hpu.db')
    cur= conn.cursor()
    sql="create table users(id Integer primary key autoincrement,account char,pwd char)"
    cur.execute(sql)
    conn.commit()
def db3():
    conn = sqlite3.connect('hpu.db')
    cur = conn.cursor()
    sql="select * from users "
    cur.execute(sql)
    rs=cur.fetchall()
    print(rs)


def db4(username,passward):
    conn = sqlite3.connect('hpu.db')
    cur = conn.cursor()
    sql=f"select * from users where account='{username}' and pwd='{passward}'"
    cur.execute(sql)
    rs=cur.fetchall()
    print(rs)
    return rs
def db6(username, password):
    conn = sqlite3.connect('hpu.db')
    cur = conn.cursor()
    try:
        # 先检查用户名是否已存在
        check_sql = f"select * from users where account='{username}'"
        cur.execute(check_sql)
        existing_user = cur.fetchall()

        if existing_user:
            print(f"用户名 '{username}' 已存在")
            return False

        # 插入新用户
        insert_sql = f"insert into users(account, pwd) values('{username}', '{password}')"
        cur.execute(insert_sql)
        conn.commit()
        print(f"用户 '{username}' 注册成功")
        return True

    except Exception as e:
        print(f"注册失败: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    db3()