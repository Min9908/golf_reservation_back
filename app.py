from flask import Flask, request, jsonify
import login_test
from flask_cors import CORS
import sqlite3
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import time
# db에 등록된 예약 정보를 확인 후 매크로 실행, 예약 정보 제거


def check_and_delete_reservations():
    try:
        current_datetime = datetime.now()
        print("Current Timestamp:", current_datetime)
        reservation_data = get_reservation_data()
        print(reservation_data)

        # 예약 정보 테이블에서 매크로 시작 날짜와 현재 날짜가 동일한 정보가 있는지 확인
        for row in reservation_data:
            date_parts = "".join(row[3].split()[:-1])
            year = date_parts.split('년')[0]

            month = date_parts.split('년')[1].split('월')[0]

            day = date_parts.split('년')[1].split('월')[1].split('일')[0]

            date_set = year + '-' + month + '-' + day

            selectedDay = datetime.strptime(date_set, '%Y-%m-%d')

            print(type(selectedDay))
            print(
                f'current_datetime: {current_datetime}, selectedDay: {selectedDay}')

            # 로그인 진행 시간을 08:59:30로 지정
            # 테스트 시에는 and 이후 제거
            # (current_datetime.day == selectedDay.day and current_datetime.hour == 8 and current_datetime.minute == 59 and current_datetime.second >= 30)  or (current_datetime.day == selectedDay.day and current_datetime.hour == 9 and current_datetime.minute <= 1)
            if(current_datetime.day == selectedDay.day and current_datetime.hour == 9 and current_datetime.minute <= 1) or (current_datetime.day == selectedDay.day and current_datetime.hour == 8 and current_datetime.minute == 59 and current_datetime.second <= 59) or (current_datetime.day == selectedDay.day and current_datetime.hour == 10 and current_datetime.minute <= 1) or (current_datetime.day == selectedDay.day and current_datetime.hour == 9 and current_datetime.minute == 59 and current_datetime.second <= 59):
                print('메크로 시작')
                # 매크로 실행(로그인)
                cookies, elapsed_time = login_test.login_test(
                    "https://www.debeach.co.kr/",
                    row[1], row[2], row[3], row[4], row[5], row[6], row[0], row[7]
                )
                # db에서 해당 예약 정보 제거
                # if (current_datetime.day == selectedDay.day and current_datetime.hour == 10 and current_datetime.minute == 1):
                #     print(current_datetime.hour)
                #     print(current_datetime.minute)
                #     delete_reservation_data(row[0])
                return str(elapsed_time), 200

    except Exception as e:
        if (current_datetime.day == selectedDay.day and current_datetime.hour == 10 and current_datetime.minute == 1):
            print(current_datetime.hour)
            print(current_datetime.minute)
            delete_reservation_data(row[0])
        print('Error:', e)


# CORS 에러 해결 코드
app = Flask(__name__)
CORS(app)


# DB에 예약 정보 추가
def insert_reservation_data(id, pw, selectedDay, nextFuture, futureTime, personnel, orderCheck):
    conn = sqlite3.connect("C:/golf_db/golf_db.db")
    cursor = conn.cursor()

    query = """

    INSERT INTO Reservation (uid, upw, selectedDay, nextFuture, futureTime, personnel, orderCheck)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(query, (id, pw, selectedDay,
                   nextFuture, futureTime, personnel, orderCheck))

    conn.commit()
    conn.close()


# 전체 테이블 정보 조회
def get_reservation_data():
    conn = sqlite3.connect("C:/golf_db/golf_db.db")
    cursor = conn.cursor()

    query = """
    SELECT * FROM Reservation
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    conn.close()
    print(f'rows: {rows}')
    return rows


# 예약 정보 제거
def delete_reservation_data(id):
    conn = sqlite3.connect("C:/golf_db/golf_db.db")
    cursor = conn.cursor()

    query = """
    DELETE FROM Reservation WHERE id=?
    """

    cursor.execute(query, (id,))

    conn.commit()
    conn.close()


def get_reservation_result_data():
    conn = sqlite3.connect("C:/golf_db/golf_db.db")
    cursor = conn.cursor()

    query = """
    SELECT * FROM ResultLog
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    conn.close()
    print(f'rows: {rows}')
    return rows


# 예약 등록 컨트롤러
@app.route('/reservation', methods=['POST'])
def reservation_route():
    try:
        print(request.form)
        id = request.form.get('id')
        pw = request.form.get('pw')
        personnel = request.form.get('personnel')
        selectedDay = request.form.get('selectedDay')
        nextFuture = request.form.get('nextFuture')
        futureTime = request.form.get('futureTime')
        orderCheck = request.form.get('orderCheck')
        insert_reservation_data(id, pw, selectedDay,
                                nextFuture, futureTime, personnel, orderCheck)

        return jsonify({'success': True}), 200

    except Exception as e:
        error_message = str(e)
        response = {'success': False, 'error': error_message}
        return jsonify(response), 500


# 예약 정보 조회 컨트롤러
@app.route('/reservation_table', methods=['GET'])
def reservation_table():
    try:
        reservation_data = get_reservation_data()

        # db 테이블 정보를 json 형태로 프론트에 반환
        reservations = []
        for row in reservation_data:
            reservation = {
                'id': row[0],
                'uid': row[1],
                'upw': row[2],
                'selectedDay': row[3],
                'nextFuture': row[4],
                'futureTime': row[5],
                'personnel': row[6],
                'orderCheck': row[7],
            }
            reservations.append(reservation)

        return jsonify({'reservations': reservations}), 200

    except Exception as e:
        error_message = str(e)
        response = {'success': False, 'error': error_message}
        return jsonify(response), 500


# DB 예약 정보 제거 컨트롤러
@app.route('/reservation_cancel/<int:id>', methods=['DELETE'])
def reservation_cancel_route(id):
    try:
        delete_reservation_data(id)

        return jsonify({'success': True}), 200

    except Exception as e:
        error_message = str(e)
        response = {'success': False, 'error': error_message}
        return jsonify(response), 500


@app.route('/reservation_result', methods=['GET'])
def reservation_result():
    try:
        result_log_data = get_reservation_result_data()

        # db 테이블 정보를 json 형태로 프론트에 반환
        resultLogData = []
        for row in result_log_data:
            resultLogDataObj = {
                'id': row[0],
                'selectedDay': row[1],
                'personnel': row[2],
                'nextFuture': row[3],
                'futureTime': row[4],
                'result': row[5],
                'course': row[6],
                'teeUpTime': row[7]
            }
            resultLogData.append(resultLogDataObj)

        return jsonify({'resultLogData': resultLogData}), 200

    except Exception as e:
        error_message = str(e)
        response = {'success': False, 'error': error_message}
        return jsonify(response), 500


# # 스케줄러 적용
scheduler = BackgroundScheduler(daemon=True)

# # 배포용 코드: 59분 30초마다 매크로 실행 가능한 예약 정보를 탐색함.
# # # 테스트용 코드: 50초가 될 때마다 스케줄링 
# scheduler.add_job(check_and_delete_reservations,
#                  'interval', seconds=50)
# set_date_time = datetime.now()
# if set_date_time.hour == 13:
#     print("123")
#     while(1):
#         scheduler.add_job(check_and_delete_reservations,
#                   trigger='cron', hour='*', minute='*', second='30')
        
#         time.sleep(30)
#         if set_date_time.minute == 42:
#             break
scheduler.add_job(check_and_delete_reservations,
                   trigger='cron', hour='*', minute='59', second='56') # 09:00:00 - 09:00:20
scheduler.add_job(check_and_delete_reservations,
                   trigger='cron', hour='*', minute='0', second='25') # 09:00:20 - 09:00:40
scheduler.add_job(check_and_delete_reservations,
                  trigger='cron', hour='*', minute='0', second='55') # 09:00:40 - 09:01:00
scheduler.add_job(check_and_delete_reservations,
                   trigger='cron', hour='*', minute='1', second='25') # 09:01:00 - 09:01:20
scheduler.start()
# scheduler.remove_all_jobs()
# check_and_delete_reservations()

if __name__ == '__main__':

    app.debug = True
    app.run(host='0.0.0.0', port=5000)
