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

        ######## 이벤트루프 모음
        self.detail_account_info_event_loop = None
        #############################

        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_commConnect()
        self.get_account_info()
        self.detail_account_info()

    def get_ocx_instance(self):
        # 키움OpenAPI 프로그램 레지스트리 등록
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.trdata_slot)

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
        # 계좌기본정보요청
        account_list = self.dynamicCall("GetLoginInfo(String)","ACCNO")
        self.account_num = account_list.split(";")[0]
        print("나의 보유 계좌번호 : %s " % self.account_num)

        self.user_id = self.dynamicCall("GetLoginInfo(String)", "USER_ID")
        print("아이디  %s " % self.user_id)

        self.user_name = self.dynamicCall("GetLoginInfo(String)", "USER_NAME")
        print("이름 : %s " % self.user_name)

    def detail_account_info(self):
        # 예수금상세현황요청
        print("---- 예수금을 요청하는 부분 ----")
        # Open API 조회 함수 입력값
        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        # Open API 조회 함수를 호출해서 전문을 서버로 전송
        # CommRqData("요청이름",  "TR번호",  "preNext",  "스크린번호")
        self.dynamicCall("CommRqData(String, String, int, String)","예수금상세현황요청","opw00001","0", "2000")

        #Event Loop 동시성 처리
        self.detail_account_info_event_loop =QEventLoop()
        self.detail_account_info_event_loop.exec()

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        '''
        tr 요청을 받는 구역, 슬롯.
        :param sScrNo: 스크린번호
        :param sRQName: 내가 요청했을 때 지은 이름
        :param sTrCode: 요청 id, tr코드
        :param sRecordName: 사용안함
        :param sPrevNext: 다음페이지가 있는지
        :return:
        '''

        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "예수금")
            print("예수금 : %s원" % format(int(deposit),","))

            ok_deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "출금가능금액")
            print("출금가능금액 : %s원" % format(int(ok_deposit),","))

            # Event Loop 동시성 처리
            self.detail_account_info_event_loop.exit()