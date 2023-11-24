from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
from custom_exception import NoAvailableSlotsException
from selenium.webdriver.common.alert import Alert
import sqlite3
import app




def find_closest_time(bk_time_list, futureTime):  # 최적시간 찾기 메서드
    # 조건: 지정시간 1시간 내외, 그 중 가장 가까운 시간 택 1
    # 이전의 시간과 병행 지정할 경우, diff 연산을 abs로 처리
    # 조건: 지정시간 2시간 내, 그 중 가장 가까운 시간 택 1
    # abs삭제, diff <= 60 비교는 얼마 시간이 경과 후 인지 확인.
    # (time - target_time).total_seconds() // 60 
    target_time = datetime.strptime(futureTime, "%H:%M")
    closest_time = None
    min_diff = float('inf')

    for time_str in bk_time_list:
        time = datetime.strptime(time_str, "%H:%M")
        if time >= target_time:
            diff = (time - target_time).total_seconds() // 60     
            
            if diff <= 120 and diff < min_diff:
                closest_time = time_str
                min_diff = diff

    return closest_time

def find_farthest_time(bk_time_list, futureTime):  # 가장 먼 시간 찾기 메서드
    # 조건: 지정시간 2시간 내, 그 중 가장 먼 시간 택 1
    target_time = datetime.strptime(futureTime, "%H:%M")
    farthest_time = None
    max_diff = 0  # 초기값을 0으로 설정

    for time_str in bk_time_list:
        time = datetime.strptime(time_str, "%H:%M")
        if time >= target_time:
            diff = (time - target_time).total_seconds() // 60
            if diff <= 120 and diff > max_diff:
                farthest_time = time_str
                max_diff = diff

    return farthest_time

# 예약 결과 로그 db에 기록
def insert_result_log(selectedDay, personnel, nextFuture, futureTime, result, course, teeUpTime):
    conn = sqlite3.connect("C:/golf_db/golf_db.db")
    cursor = conn.cursor()

    query = """

    INSERT INTO ResultLog (selectedDay, personnel, nextFuture, futureTime, result, course, teeUpTime)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(query, (selectedDay, personnel, nextFuture,
                   futureTime, result, course, teeUpTime))

    conn.commit()
    conn.close()


def reservation_test(driver, target_day, elements, target_month, futureTime, personnel, selectedDay, nextFuture, tid, order):
    print("reservation_test module open!")
    check_time = datetime.now()
    for element in elements:

        h2_elements = element.find_elements(By.TAG_NAME, 'h2')
        for h2_element in h2_elements:
            h2_text = h2_element.text

            if target_month+'월' in h2_text:
                print(h2_text)
                table_element = h2_element.find_element(
                    By.XPATH, './following-sibling::table')

                td_elements = table_element.find_elements(
                    By.XPATH, './/td[@class="  "]')
                print('success to finding td_elements!')
                for td_element in td_elements:
                    a_elements = td_element.find_elements(
                        By.TAG_NAME, 'a')
                    for a_element in a_elements:
                        a_text = a_element.text

                        if str(target_day) in a_text:
                            print('trying to find table..')
                            try:
                                td_element.click()
                            except Exception as error:
                                # if isWednesday:
                                #     print('exception 테스트-------------------')
                                #     closeBtn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                                #         (By.XPATH, '//*[@id="modal-view"]/div/div/div[1]/button/span/i')))
                                #     closeBtn.click()
                                #     return
                                print(error)
                                insert_result_log(
                                    selectedDay, personnel, nextFuture, futureTime, '실패', 'X', 'X')
                                driver.close()
                                return error, 500

                            print('successed to finding reservable day!')
                            elements = driver.find_element(
                                By.CLASS_NAME, 'col-xs-7')

                           # 첫번째 예약 버튼 로드까지 기다림
                            try:
                                tr_elements_load = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                                    (By.XPATH, '//*[@id="booking-index"]/div[2]/div[2]/div/table/tbody/tr[1]/td[5]/button[1]')))
                            except Exception as error:
                                # if isWednesday:
                                #     print('exception 테스트-------------------')
                                #     closeBtn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                                #         (By.XPATH, '//*[@id="modal-view"]/div/div/div[1]/button/span/i')))
                                #     closeBtn.click()
                                #     return
                                print(error)
                                insert_result_log(
                                    selectedDay, personnel, nextFuture, futureTime, '실패', 'X', 'X')
                                driver.close()
                                return error, 500

                            time_tbody = elements.find_element(
                                By.XPATH, '//*[@id="booking-index"]/div[2]/div[2]/div/table/tbody')
                            tr_elements = time_tbody.find_elements(
                                By.TAG_NAME, "tr")
                            bk_time_list = []
                            td_elements_list = []

                            for tr in tr_elements:
                                td_elements = tr.find_elements(
                                    By.CLASS_NAME, "bk_time")
                                td_elements_list.extend(td_elements)
                                for td in td_elements:
                                    strong_element = td.find_element(
                                        By.TAG_NAME, "strong")
                                    bk_time_list.append(strong_element.text)

                            print("bk_time_list:", bk_time_list)
                            if order == '1':
                                closest_time = find_closest_time(
                                    bk_time_list, futureTime)
                                print(order + "가장 가까운 것")
                            else:
                                closest_time = find_farthest_time(
                                    bk_time_list, futureTime)
                                print(order + "가장 먼 것")
                            if closest_time is not None:
                                print("Closest time:", closest_time)
                            else:
                                print("There is no available time slot.")
                                insert_result_log(
                                    selectedDay, personnel, nextFuture, futureTime, '실패', 'X', 'X')
                                return

                            # 가장 가까운 시간의 tr요소에서 예약 버튼 찾아서 클릭
                            for tr in tr_elements:
                                td_element = tr.find_element(
                                    By.CLASS_NAME, "bk_time")
                                strong_element = td_element.find_element(
                                    By.TAG_NAME, "strong")
                                closest_time = str(closest_time)
                                if closest_time == strong_element.text:
                                    print('find matched value!')
                                    reservation_btn = tr.find_elements(
                                        By.TAG_NAME, "button")[0]
                                    course = tr.find_element(
                                        By.CLASS_NAME, "bk_cours").text
                                    print('course: ' + course)
                                    reservation_btn.click()
                                    print("예약버튼 클릭했나..")

                                    # 인원 수 체크
                                    radio_element = WebDriverWait(driver, 5).until(
                                        EC.element_to_be_clickable((By.XPATH, '//*[@id="form-create"]/div[6]/div')))
                                    print(radio_element)
                                    if personnel == '3':
                                        print("예약 페이지에 접속했나?..")
                                        cnt3 = radio_element.find_element(
                                            By.XPATH, '//*[@id="form-create"]/div[6]/div/label[1]')
                                        cnt3.click()
                                    else:
                                        print("예약 페이지에 접속했나?..")
                                        cnt4 = radio_element.find_element(
                                            By.XPATH, '//*[@id="form-create"]/div[6]/div/label[2]')
                                        cnt4.click()

                                    submit_btn = driver.find_element(
                                        By.XPATH, '//*[@id="form-create"]/div[9]/button[1]')
                                    submit_btn.click()

                                    # 모달창이 나타나는 부분
                                    try:
                                        alert1 = WebDriverWait(driver, 5).until(
                                            EC.alert_is_present())
                                        print("모달창이 나왔나?")
                                        alert1.accept()
                                        print("모달창 확인 버튼 클릭 완료!")

                                        try:

                                            print("예약 완료 테이블 탐색중...")
                                            reservation_result_table = WebDriverWait(driver, 5).until(
                                                EC.presence_of_element_located(
                                                    (By.XPATH, '//*[@id="booking-history"]/table[1]'))
                                            )
                                            print("예약 완료!")
                                            print(check_time)
                                            insert_result_log(
                                                selectedDay, personnel, nextFuture, futureTime, '성공', course, closest_time)
                                            reservation_data = app.get_reservation_data()
                                            app.delete_reservation_data(tid)
                                            return "예약 성공"

                                        except Exception as error:
                                            # if isWednesday:
                                            #     closeBtn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                                            #         (By.XPATH, '//*[@id="modal-view"]/div/div/div[1]/button/span/i')))
                                            #     closeBtn.click()
                                            #     return
                                            print(error)
                                            insert_result_log(
                                                selectedDay, personnel, nextFuture, futureTime, '실패', 'X', 'X')
                                            driver.close()
                                            return error, 500

                                    except Exception as error:
                                        # if isWednesday:
                                        #     print(
                                        #         'exception 테스트-------------------')
                                        #     return
                                        print(error)
                                        print("여기서 오류 발생하면 TRY도 못해보는거")
                                        insert_result_log(
                                            selectedDay, personnel, nextFuture, futureTime, '실패', 'X', 'X')
                                        driver.close()
                                        return error, 500

                else:
                    print('cannot find matched a_text.. ㅜ.ㅜ')
                    # if isWednesday:
                    #     print('exception 테스트-------------------')
                    #     return
                    # else:
                    insert_result_log(
                        selectedDay, personnel, nextFuture, futureTime, '실패', 'X', 'X')
                    driver.close()
                    raise NoAvailableSlotsException(
                        '해당 날짜에 예약 가능한 시간대가 없습니다.')

        # if target_month in h2_text:
        #     break
