# test_db_connection.py
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# 실제로 뭐가 로드되는지 확인
print("=== 환경변수 확인 ===")
print(f"host: [{os.environ.get('host')}]")
print(f"port: [{os.environ.get('port')}]")
print(f"user: [{os.environ.get('user')}]")
print(f"passwd: [{os.environ.get('passwd')}]")
print(f"dbname: [{os.environ.get('dbname')}]")
print("=" * 50)

try:
    conn = pymysql.connect(
        host='192.168.60.129',
        user="crawler",
        password="jbnuezen1!",
        database="bigdata",
        port=3306
    )
    print("✅ DB 연결 성공!")
    
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    print(f"📋 테이블 목록:")
    for table in tables:
        print(f"  - {table[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM store;")
    count = cursor.fetchone()[0]
    print(f"📊 store 테이블 데이터 수: {count}개")
    
    conn.close()
    print("\n✅ 모든 테스트 통과!")
    
except Exception as e:
    print(f"❌ DB 연결 실패!")
    print(f"에러: {e}")
    print("\n확인사항:")
    print("1. 서버에서 MySQL이 실행 중인가?")
    print("2. bind-address를 0.0.0.0으로 변경했는가?")
    print("3. MySQL을 재시작했는가?")
    print("4. 외부 접속 계정을 생성했는가?")
    print("5. SSH 터널링을 실행했는가? (방법1 사용시)")