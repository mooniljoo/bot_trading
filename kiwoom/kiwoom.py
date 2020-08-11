from PyQt5.QAxContainer import *
from PyQt5.QtCore import *


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        print("Kiwoom 클래스입니다.")

        ######## eventloop 모듈
        self.login_next_loop = None
        #############################

        ######## 변수 모음
        self.account_num = None
        self.user_id = None
        self.user_name = None
        #############################

        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_commConnect()
        self.get_account_info()

    def get_ocx_instance(self):
        # 키움OpenAPI 프로그램 레지스트리 등록
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)

    def login_slot(self, errCode):
        # errCode가 0일 때 실행
        print(errCode)

        self.login_event_loop.exit()

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    # 로그인 에러 처리
    def login_slot(self, errCode):
        print(Exception(errCode))

        self.login_event_loop.exit()

    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(String)","ACCNO")
        self.account_num = account_list.split(";")[0]
        print("나의 보유 계좌번호 : %s " % self.account_num)

        self.user_id = self.dynamicCall("GetLoginInfo(String)", "USER_ID")
        print("아이디  %s " % self.user_id)

        self.user_name = self.dynamicCall("GetLoginInfo(String)", "USER_NAME")
        print("이름 : %s " % self.user_name)
