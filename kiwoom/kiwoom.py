from PyQt5.QAxContainer import *
from PyQt5.QtCore import *


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        print("Kiwoom 클래스입니다.")

        ######## eventloop 모듈
        self.login_next_loop = None
        self.detail_account_info_event_loop = None
        self.detail_account_info_event_loop_2 = None
        #############################

        ######## 변수 모음
        self.account_num = None
        self.user_id = None
        self.user_name = None
        #############################

        ######## 계좌 관련 변수
        self.use_money = 0
        self.use_money_percent = 0.5
        #############################

        ######## 변수 모음
        self.account_stock_dict = {}
        #############################

        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_commConnect()
        self.get_account_info()
        self.detail_account_info() #예수금 요청
        self.detail_account_mystock() #보유종목 요청

    def get_ocx_instance(self):
        # 키움OpenAPI 프로그램 레지스트리 등록
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.trdata_slot)

    def login_slot(self, errCode):
        # errCode 가 0일 때 실행
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
        self.dynamicCall("CommRqData(String, String, int, String)", "예수금상세현황요청", "opw00001", "0", "2000")

        # Event Loop 동시성 처리
        self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec()

    def detail_account_mystock(self, sPrevNext="0"):
        #계좌평가잔고내역요청
        print("---- 계좌평가잔고내역을 요청하는 부분 ----")
        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        # Open API 조회 함수를 호출해서 전문을 서버로 전송
        self.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "opw00018", sPrevNext, "2000")

        # Event Loop 동시성 처리
        self.detail_account_info_event_loop_2 = QEventLoop()
        self.detail_account_info_event_loop_2.exec()

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

            # 한 종목 구입랼
            self.use_money = int(deposit) * self.use_money_percent
            self.use_money = self.use_money / 4



            ok_deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "출금가능금액")
            print("출금가능금액 : %s원" % format(int(ok_deposit),","))

            # Event Loop 동시성 처리
            self.detail_account_info_event_loop.exit()

        if sRQName == "계좌평가잔고내역요청":
            total_buy_money = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총매입금액")
            print("총 매입금액 : %s원" % format(int(total_buy_money), ","))

            total_profit_loss_rate = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총수익률(%)")
            print("총 수익률 : %s%%" % float(total_profit_loss_rate))

            # 보유 종목
            # 종목 보유 갯수 확인
            rows = self.dynamicCall("GetRepeatCnt(QString ,QString)", sTrCode, sRQName)
            # 0은 첫 번째 종목, 1은 두 번째 종목···
            cnt = 0
            for i in range(rows):
                # A:장내주식, J:ELW종목, Q:ETN종목
                code = self.dynamicCall("GetCommData(QString, QString, int, QString", sTrCode, sRQName, i, "종목번호")
                code = code.strip()[1:]

                code_name = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"종목명")
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")

                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict.update({code:{}})

                code_name = code_name.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity)

                self.account_stock_dict[code].update({"종목명": code_name})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액": total_chegual_price})
                self.account_stock_dict[code].update({"매매가능수량": possible_quantity})

                cnt += 1

            print("보유 종목 수 : %s개" % cnt)
            print("보유 종목 : %s" % self.account_stock_dict)


            # Event Loop 동시성 처리
            self.detail_account_info_event_loop_2.exit()