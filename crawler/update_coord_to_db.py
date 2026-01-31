import pandas as pd
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# 가게 좌표 업데이트 함수 -> coord_included.csv 파일 사용 -> DB 반영
# coord_included.csv 파일은 get_coord_from_csv.py에서 생성됨
# 사용자에게 좌표 없는 가게 제외 여부 확인 (모든 가게에 좌표가 있다면 바로 저장)

def update_store_coordinates(csv_path="coord_included.csv"):
    conn = None
    cursor = None
    load_dotenv()
    try:
        # 1. CSV 로드 (인코딩 처리)
        print(f"📂 CSV 파일 로드 중: {csv_path}")
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        print(f"총 {len(df)}개 행 로드")
        
        # 2. 좌표 없는 가게 체크 및 사용자 확인
        missing_coords = df[df[['lat', 'lng']].isna().any(axis=1)]
        if not missing_coords.empty:
            print(f"\n⚠️  좌표 없는 가게 {len(missing_coords)}개 발견:")
            print("-" * 80)
            for idx, row in missing_coords.iterrows():
                print(f"  [{row['s_idx']}] {row['s_address']}")
            print("-" * 80)
            
            response = input(f"\n이 {len(missing_coords)}개 가게를 제외하고 진행할까요? (y: 제외하고 진행 / n: 전체 취소): ")
            if response.lower() != 'y':
                print("❌ 업데이트 취소")
                return
            
            # 사용자가 y를 누르면 NaN 제거
            df = df.dropna(subset=["s_idx", "lat", "lng"])
            print(f"\n✅ 좌표 없는 가게 {len(missing_coords)}개 제외")
        
        print(f"✅ 업데이트 대상: {len(df)}개")
        
        # 3. 데이터 검증
        if df.empty:
            print("❌ 업데이트할 데이터가 없습니다.")
            return
        
        # s_idx가 정수인지 확인
        df['s_idx'] = df['s_idx'].astype(int)
        
        # 4. DB 연결
        print("\n🔌 DB 연결 중...")
        conn = mysql.connector.connect(
            host=os.environ.get('host'),
            user=os.environ.get('user'),
            password=os.environ.get('passwd'),
            database=os.environ.get('dbname'),
            port=int(os.environ.get('port', 3306))
        )
        cursor = conn.cursor()
        print("✅ DB 연결 성공")
        
        # 5. 업데이트 전 기존 데이터 확인 (선택사항)
        sample_idx = df['s_idx'].iloc[0]
        cursor.execute(
            "SELECT s_idx, s_y_coord, s_x_coord FROM store WHERE s_idx = %s",
            (int(sample_idx),)
        )
        before = cursor.fetchone()
        if before:
            print(f"\n예시) s_idx={before[0]} - 기존 좌표: ({before[1]}, {before[2]})")
        
        # 6. UPDATE 쿼리 준비
        sql = """
        UPDATE store
        SET
            s_y_coord = %s,
            s_x_coord = %s
        WHERE s_idx = %s
        """
        
        # executemany용 데이터 생성
        data = [
            (row["lat"], row["lng"], int(row["s_idx"]))
            for _, row in df.iterrows()
        ]
        
        # 7. 일괄 실행
        print(f"\n🔄 {len(data)}개 가게 좌표 업데이트 중...")
        cursor.executemany(sql, data)
        conn.commit()
        
        print(f"✅ {cursor.rowcount}개 가게 좌표 업데이트 완료")
        
        # 8. 업데이트 후 확인
        cursor.execute(
            "SELECT s_idx, s_y_coord, s_x_coord FROM store WHERE s_idx = %s",
            (int(sample_idx),)
        )
        after = cursor.fetchone()
        if after:
            print(f"예시) s_idx={after[0]} - 업데이트 후: ({after[1]}, {after[2]})")
        
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {csv_path}")
    except Error as e:
        print(f"❌ DB 오류: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        if conn:
            conn.rollback()
    finally:
        # 9. 종료
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("\n🔚 프로그램 종료")

if __name__ == "__main__":
    update_store_coordinates()