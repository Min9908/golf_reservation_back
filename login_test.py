from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime, timedelta
from reservation import reservation_test
from custom_exception import NoAvailableSlotsException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service as ChromeService

# 08:59:30에 로그인이 진행되었으면 09:00:00까지 대기함



def wait_until_9_am():
    while True:
        current_time = datetime.now().time()
        # or (current_time.hour == 15 and current_time.second == 00)
        if (current_time.hour == 9) or (current_time.hour == 10):
            break


def login_test(url, id, pw, selectedDay, nextFuture, futureTime, personnel, tid, order):

    options = Options()  # 크롬 드라이버 자동 설치 적용됨. 최신 버전으로 항상 호환성 유지됨
    options.add_argument('--disable-gpu')  # Disable GPU acceleration
    options.add_argument('--no-sandbox')  # Disable the sandbox mode
    options.add_argument('--disable-extensions')  # Disable extensions
    # Disable shared memory usage
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--start-fullscreen')  # 전체화면  

    # driver = webdriver.Chrome(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))

    driver.get(url)

    # 만약 드비치 홈페이지에 윈도우 폼 형태의 팝업이 생길 경우 필요한 코드
    # tabs = driver.window_handles
    # print(tabs)
    # while len(tabs) != 1:
    #     driver.switch_to_window(tabs[1])
    #     driver.close()

    # 사이트 상단의 Login 버튼 클릭
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '/html/body/header/div[1]/div/div[3]'))
    )

    element.click()
    print(futureTime)

    #  ID ,PW 정보로 로그인 시도
    username_field = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="content-main"]/form/div/div[1]/div[3]/div[1]/ul/li[1]/div/input'))
    )
    password_field = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="content-main"]/form/div/div[1]/div[3]/div[1]/ul/li[2]/div/input'))
    )

    username_field.send_keys(id)
    password_field.send_keys(pw)

    # 로그인 버튼 클릭
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="content-main"]/form/div/div[1]/div[3]/div[2]/div/button'))
    )
    current_url = driver.current_url
    login_button.click()
    cookies = driver.get_cookies()
    # 로그인 에러처리
    time.sleep(1)
    if current_url == driver.current_url:
        print("Login failed. The domain after the click is: ", current_url)
        driver.close()
        raise Exception(
            "로그인 실패! 아이디 비밀번호를 확인해주세요.")

    # 시간측정 시작
    start_time = time.time()
    

    # 현재시간이 9시가 될때까지 대기
    wait_until_9_am()
    reservation_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="content-main"]/div[1]/div[5]/div[2]/div/h3/a[1]'))
    )
    driver.execute_script("arguments[0].click();", reservation_btn)

    elements = driver.find_elements(By.CLASS_NAME, 'col-xs-5')
    # if wednesdayCheck == '3':  # 수요일 예약의 경우
    #     print("수요일 예약 선택")

    #     print("1. 14일 뒤 수요일 예약 진행")
    #     isWednesday = True
    #     # 14일 뒤 수요일 예약 진행
    #     year = int(nextFuture.split('년')[0].strip())
    #     month = int(nextFuture.split('년')[1].split('월')[0].strip())
    #     day = int(nextFuture.split('월')[1].split('일')[0].strip())

    #     target_date = datetime(year, month, day)
    #     target_month = target_date.strftime("%m")
    #     target_day = int(target_date.strftime("%d"))
    #     print(target_month, target_day)
    #     if reservation_test(driver, target_day, elements,
    #                         target_month, futureTime, personnel, isWednesday) == "예약 성공":
    #         driver.close()
    #         end_time = time.time()
    #         elapsed_time = end_time - start_time
    #         return cookies, elapsed_time

    #     print("2. 10일 뒤 토요일 예약 진행")
    #     year = int(nextSaturday.split('년')[0].strip())
    #     month = int(nextSaturday.split('년')[1].split('월')[0].strip())
    #     day = int(nextSaturday.split('월')[1].split('일')[0].strip())

    #     target_date = datetime(year, month, day)
    #     target_month = target_date.strftime("%m")
    #     target_day = int(target_date.strftime("%d"))
    #     print(target_month, target_day)
    #     if reservation_test(driver, target_day, elements,
    #                         target_month, saturdayTime, personnel, isWednesday) == "예약 성공":
    #         driver.close()
    #         end_time = time.time()
    #         elapsed_time = end_time - start_time
    #         return cookies, elapsed_time

    #     print("3. 11일 뒤 일요일 예약 진행")
    #     year = int(nextSunday.split('년')[0].strip())
    #     month = int(nextSunday.split('년')[1].split('월')[0].strip())
    #     day = int(nextSunday.split('월')[1].split('일')[0].strip())

    #     target_date = datetime(year, month, day)
    #     target_month = target_date.strftime("%m")
    #     target_day = int(target_date.strftime("%d"))
    #     print(target_month, target_day)
    #     if reservation_test(driver, target_day, elements,
    #                         target_month, sundayTime, personnel, isWednesday) == "예약 성공":
    #         driver.close()
    #         end_time = time.time()
    #         elapsed_time = end_time - start_time
    #         return cookies, elapsed_time

    #     driver.close()
    #     raise NoAvailableSlotsException('모든 날짜의 예약에 실패했습니다... 예약 가능 날짜가 없습니다.')

    # else:  # 수요일 아닌 경우
    # isWednesday = False
    year = int(nextFuture.split('년')[0].strip())
    month = int(nextFuture.split('년')[1].split('월')[0].strip())
    day = int(nextFuture.split('월')[1].split('일')[0].strip())

    target_date = datetime(year, month, day)
    target_month = target_date.strftime("%m")
    target_day = int(target_date.strftime("%d"))
    print(target_month, target_day)
    reservation_test(driver, target_day, elements,
                     target_month, futureTime, personnel, selectedDay, nextFuture, tid, order)

    # 주말의 경우는 프론트에서 예외처리를 해두었음.

    # 시간측정한 값과 함께 반환
    driver.close()
    end_time = time.time()
    elapsed_time = end_time - start_time
    return cookies, elapsed_time