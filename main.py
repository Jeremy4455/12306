import requests
import settings
import urllib3
from selenium.webdriver import Edge, ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep

urllib3.disable_warnings()


class LeftQuery:
    def __init__(self):
        self.station_url = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9235"
        self.query_url = "https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT"

    def get_station(self, station):
        response = requests.get(url=self.station_url, headers=settings.headers).text
        result = response.split('@')[1:]
        temp_dict = {}
        for i in result:
            temp_str = i.split("|")
            temp_dict[temp_str[1]] = temp_str[2]
        try:
            return temp_dict[station]
        except:
            print("没有找到" + station + "车站")
            raise

    def query(self, from_station, to_station, date):
        url = self.query_url.format(date, self.get_station(from_station), self.get_station(to_station))
        response = requests.get(url=url, headers=headers).json()
        result = response['data']['result']
        if result is None:
            print("抱歉，没有符合条件的列车！")
            exit()
        else:
            print(date + "\n" + from_station + "-" + to_station + "查询成功")
            seat = {32: "商务座特等座", 31: "一等座", 30: "二等座", 21: "高级软卧", 23: "软卧", 26: "无座", 28: "硬卧", 29: "硬座", 33: "动卧", }
            for i in result:
                temp = i.split("|")
                if temp[0] != "" and temp[0] != "null":
                    print("车次" + temp[3] + "，出发时间：" + temp[8] + " 到达时间：" + temp[9], end=" ")
                for j in seat.keys():
                    if temp[j] != "无" and temp[j] != "":
                        if temp[j] == "有":
                            print(seat[j] + "有票 ", end="")
                        else:
                            print(seat[j] + "有" + temp[j] + "张票 ", end="")
                print("")
        return result


def login():
    driver = Edge()
    driver.maximize_window()
    driver.get("https://kyfw.12306.cn/otn/resources/login.html")
    # 防止网站禁用selenium
    script = "Object.defineProperty(navigator, 'webdriver', {get:()=>undefined, });"
    driver.execute_script(script)
    sleep(1)
    # 账号登录
    search_login = driver.find_element(by="css selector", value='ul[class="login-hd"] li[class="login-hd-code active"]')
    search_login.click()
    # 输入用户名和密码
    input_username = driver.find_element(by="css selector",
                                         value='div[class="login-item"] input[placeholder="用户名/邮箱/手机号"]')
    input_password = driver.find_element(by="css selector", value='div[class="login-item"] input[placeholder="密码"]')
    input_username.send_keys(username)
    input_password.send_keys(password)
    sleep(2)
    search_login = driver.find_element(by="css selector", value='div[class="login-btn"] a[id="J-login"]')
    search_login.click()
    sleep(5)
    try:
        huakuai = driver.find_element(by="css selector", value='div[class="nc_scale"] span')
        action = ActionChains(driver)
        action.click_and_hold(huakuai).perform()
        action.move_by_offset(300, 0)
        action.release().perform()
        sleep(2)
    except:
        pass
    return driver


def order(from_station, to_station, date):
    query = LeftQuery()
    query.query(from_station, to_station, date)
    driver = login()
    pop = driver.find_element(by="css selector", value='div[class="modal-ft"] a')
    pop.click()
    sleep(2)
    home_page = driver.find_element(by="css selector", value='ul[class="nav"] li[id="J-index"]')
    home_page.click()
    sleep(2)
    fs_text = driver.find_element(by="css selector",
                                  value='div[class="input-box input-city"] input[id="fromStationText"]')
    ts_text = driver.find_element(by="css selector",
                                  value='div[class="input-box input-city"] input[id="toStationText"]')
    date_text = driver.find_element(by="css selector", value='div[class="input-box input-data"] input[id="train_date"]')
    # 输入出发地
    fs_text.click()
    fs_text.send_keys(from_station)
    fs_text.send_keys(Keys.ENTER)
    # 输入目的地
    ts_text.click()
    ts_text.send_keys(to_station)
    ts_text.send_keys(Keys.ENTER)
    # 输入出发日期
    driver.find_element(by="css selector", value='div[class="input-box input-data"] i[class="icon icon-date"]').click()
    # date_text.click()
    date_text.send_keys(date)
    # 点击查询
    button = driver.find_element(by="css selector", value='div[class="form-item form-item-btn"] a[id="search_one"]')
    sleep(2)
    button.click()
    while True:
        sleep(1)


if __name__ == "__main__":
    fs = settings.from_station
    ts = settings.to_station
    date = settings.date
    username = settings.username
    password = settings.password
    headers = settings.headers
    order(fs, ts, date)
