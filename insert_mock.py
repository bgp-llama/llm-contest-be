from app.database import Document, Chatbot

# ===== 목데이터 =====
SEED = [
    {
        "name": "학사 일정 도우미",
        "description": "학사 일정, 등록/휴복학, 수강신청, 성적확인, 졸업요건 등 학사 전반 안내",
        "model_name": "gpt-4o",
        "system_prompt": "당신은 대학 학사제도를 잘 아는 비서입니다. 날짜/절차/제한조건을 명확히 안내하세요.",
        "documents": [
            {
                "filename": "academic_calendar_guide.pdf",
                "file_type": "pdf",
                "content": """[학사 일정 종합 안내]
- 정규학기: 1학기(3~6월), 2학기(9~12월)
- 수강신청: 정정 포함 2주간, 신입생/재학생 순차 오픈
- 성적입력·정정: 종강 후 2주 내, 확정 후 포털 고지
- 휴학/복학: 일반·군휴학 가능, 복학원은 개강 2주 전까지
- 졸업요건: 전공/교양/균형교양 기준학점 충족 + 핵심교양 이수 + 졸업평가(논문/시험/프로젝트 중 택1)

[자주 묻는 질문]
Q. 졸업유예 가능한가요?
A. 가능. 졸업요건 충족 상태에서 유예 신청(학기 단위). 등록금은 유예 등록금 기준.
Q. 초과학기 등록금은?
A. 수강학점에 따라 차등(0~3학점/4~6학점/7학점 이상 구간).""",
            }
        ],
    },
    {
        "name": "수강신청·시간표 도우미",
        "description": "전공/교양 추천과 시간표 자동 구성, 선수과목·수업시간 충돌 점검",
        "model_name": "gpt-4o",
        "system_prompt": "사용자 전공/학년/이수상황을 바탕으로 시간표를 충돌 없이 설계하세요.",
        "documents": [
            {
                "filename": "registration_rules.pdf",
                "file_type": "pdf",
                "content": """[수강신청 규정]
- 최대/최소 학점: 18/12학점(학과 규정에 따라 상이)
- 선수과목: 전산개론 → 자료구조 → 알고리즘 순서 권장
- 중복/충돌: 요일/교시가 겹치면 신청 불가, 실습·세미나는 예외 없음
[추천 전략]
1) 전공필수 우선 배치
2) 교양은 도메인 분산(글쓰기/외국어/수리/인문)
3) 강의평가 4.0↑ 우선 검토
[TIP] 인기과목 대기: 정정기간 첫날 09:00 재시도 권장""",
            }
        ],
    },
    {
        "name": "도서관 길잡이",
        "description": "대출/반납/연장, 상호대차, 전자자료(구독 DB) 이용, 좌석예약 안내",
        "model_name": "gpt-4o",
        "system_prompt": "도서관 규정과 이용시간, 전자자원 접근법을 정확히 지도하세요.",
        "documents": [
            {
                "filename": "library_user_guide.pdf",
                "file_type": "pdf",
                "content": """[도서관 이용 안내]
- 운영시간: 학기중 평일 09:00~22:00, 시험기간 24시
- 대출권수/기간: 학부생 7권/14일, 대학원 15권/30일
- 연장: 반납기한 3일 전까지 1회(예약자 있으면 불가)
- 연체료: 1권당 1일 200원, 최대 1만원
- 전자자료: 구독 DB는 교내 IP 또는 VPN 접속 필요
- 상호대차: 소속도서관에 신청(평균 3~5일 소요)
[FAQ]
Q. 분실 시?
A. 동일 자료 변상 또는 시가 변상 + 행정수수료.""",
            }
        ],
    },
    {
        "name": "식단표·시설 안내",
        "description": "교내 식당/카페 식단, 가격, 운영시간, 휴무; 체육관/열람실 등 시설 운영",
        "model_name": "gpt-4o",
        "system_prompt": "요일/시간대별 식단과 시설 이용 혼잡도를 안내하세요.",
        "documents": [
            {
                "filename": "dining_and_facilities.pdf",
                "file_type": "pdf",
                "content": """[식당 안내]
- 학생식당: 평일 11:00~14:00/17:00~19:00 (주메뉴 4,000~5,500원)
- 교직원식당: 평일 11:30~13:30 (정식 6,500원)
- 카페: 평일 08:30~19:00, 토 10:00~15:00
[시설 안내]
- 열람실: 24시간, 좌석 배정 앱 필수
- 체육관: 평일 09:00~21:00, 주말 예약제
- 스터디룸: 2시간 단위 예약, 노쇼 2회 시 1주 제한""",
            }
        ],
    },
    {
        "name": "캠퍼스 길찾기",
        "description": "건물·강의실 코드 해석, 이동 경로, 셔틀·주차 안내",
        "model_name": "gpt-4o",
        "system_prompt": "지번·건물코드·층/호수 포맷을 이해하고 최단경로를 설명하세요.",
        "documents": [
            {
                "filename": "wayfinding_faq.pdf",
                "file_type": "pdf",
                "content": """[지름길]
- 음대에서 기숙사 가는 길 : 음대 윗 법대쪽에서 기숙사가거나 아래로 내려와서 미술대에서 가는 길
                """,
            }
        ],
    },
    {
        "name": "장학금 상담",
        "description": "교내/교외 장학금 유형, 신청기간, 성적·소득 조건, 서류 안내",
        "model_name": "gpt-4o",
        "system_prompt": "조건 매칭과 제출서류 체크리스트를 만들어 안내하세요.",
        "documents": [
            {
                "filename": "scholarship_guide.pdf",
                "file_type": "pdf",
                "content": """[장학 유형]
- 성적우수, 근로, 기초/차상위, 특별(봉사/리더십)
[신청 공통]
- 성적: 직전학기 12학점/평점 3.0↑(유형에 따라 상이)
- 소득: 한국장학재단 소득분위 기준 확인
- 서류: 성적증명서, 통장사본, 가족관계증명서(해당 시)
[근로장학]
- 근무시간 주 10~12시간, 시급 교내 기준 적용""",
            }
        ],
    },
    {
        "name": "기숙사 안내",
        "description": "입사/퇴사 절차, 호실 배정, 면학·소방 규정, 벌점/상벌점",
        "model_name": "gpt-4o",
        "system_prompt": "안전/생활 규정을 명확히. 야간통금·무단외박 등 위반사례를 주의 환기.",
        "documents": [
            {
                "filename": "dormitory_handbook.pdf",
                "file_type": "pdf",
                "content": """[입사]
- 제출: 건강진단서(결핵 검사 포함), 개인정보 동의서
- 배정: 성별/학년/거리/장애 여부 고려한 무작위
[생활 규정]
- 소음: 22:00~07:00 정숙
- 취사/전열: 화재위험 기기 반입 금지(전기장판/전기히터 제한)
- 외부인 출입: 사전 등록 필요
[벌점]
- 무단외박 5점, 실내흡연 10점(퇴사 조치), 소방설비 훼손 10점
[퇴사]
- 퇴실점검(비품/청결) 후 키 반납, 보증금 정산 7일 이내""",
            }
        ],
    },
    {
        "name": "IT 헬프데스크",
        "description": "포털/이메일/와이파이/VPN/강의녹화/소프트웨어 라이선스 지원",
        "model_name": "gpt-4o",
        "system_prompt": "문제 재현 절차와 체크리스트(운영체제/브라우저/에러메시지)를 먼저 수집.",
        "documents": [
            {
                "filename": "it_helpdesk_runbook.pdf",
                "file_type": "pdf",
                "content": """[공통 점검]
1) OS/브라우저 버전
2) 학번/사번 인증 여부
3) 오류 스크린샷/시간대
[VPN]
- 클라이언트 버전 최신화, 프로필 재설정, MFA 토큰 동기화
[무선랜]
- eduroam SSID, 기관 계정형식 user@univ.ac.kr, EAP-TTLS/PAP""",
            }
        ],
    },
    {
        "name": "시설물 고장 접수",
        "description": "강의실/연구실의 전기·수도·냉난방·비품 고장 신고 및 처리 현황",
        "model_name": "gpt-4o",
        "system_prompt": "장소코드·고장유형·사진을 받아 티켓 생성, 예상 처리기한 안내.",
        "documents": [
            {
                "filename": "facilities_sop.pdf",
                "file_type": "pdf",
                "content": """[접수 프로세스]
요청등록 → 담당배정(전기/설비/목공) → 현장점검 → 수리/교체 → 완료확인
[우선순위]
- 긴급(누수/정전/가스): 2시간 내 출동
- 보통(비품교체/경미수리): 3영업일
[필수정보] 위치(건물/호실), 증상, 사진, 연락처""",
            }
        ],
    },
    {
        "name": "취업·진로 상담",
        "description": "채용정보, 자소서/포트폴리오 코칭, 면접 대비, 인턴십/현장실습",
        "model_name": "gpt-4o",
        "system_prompt": "직무/산업별 채용 트렌드를 반영하고, 이력서 키워드를 제안.",
        "documents": [
            {
                "filename": "career_center_playbook.pdf",
                "file_type": "pdf",
                "content": """[준비 로드맵]
- 1학년: 전공탐색/동아리/기초자격
- 2학년: 프로젝트/대외활동/기술스택
- 3학년: 인턴십/자격증/영어
- 4학년: 포트폴리오 완성/면접
[자소서 팁] STAR 기법(상황-과제-행동-결과)로 구체화""",
            }
        ],
    },
    {
        "name": "연구지원 챗봇",
        "description": "연구비 집행, 시약/장비 구매, 안전교육, 공유장비 예약",
        "model_name": "gpt-4o",
        "system_prompt": "규정집의 예외조항(소액/긴급구매)과 안전수칙을 강조.",
        "documents": [
            {
                "filename": "research_admin_guide.pdf",
                "file_type": "pdf",
                "content": """[연구비 집행]
- 집행 범위: 인건비/재료비/장비유지/학회비
- 영수증/세금계산서 필수, 카드 사용 원칙
[장비 예약]
- 공용장비 포털, 안전교육 이수 후 사용 가능
[안전]
- 화학물질 관리: MSDS 비치, 폐시약 분리 배출""",
            }
        ],
    },
    {
        "name": "국제교류·유학생 지원",
        "description": "교환학생 파견/유치, 비자/보험, 한국어과정, 글로벌 프로그램",
        "model_name": "gpt-4o",
        "system_prompt": "국가·학기·어학요건을 확인하고, 서류 마감일을 강조.",
        "documents": [
            {
                "filename": "intl_office_faq.pdf",
                "file_type": "pdf",
                "content": """[교환학생 파견]
- 요건: 평점 3.0↑, 어학 성적(영어/현지어), 추천서
- 학점인정: 사전승인 과목만, 성적표 제출 필수
[유학생 지원]
- 비자 연장, 건강보험, 외국인등록증, 기숙사 우선 배정""",
            }
        ],
    },
    {
        "name": "등록금·장부/재무",
        "description": "등록금 고지/분납/연체, 반환 규정, 수입지출 증빙 안내",
        "model_name": "gpt-4o",
        "system_prompt": "납부기한/감면/환불 규정을 정확히. 케이스별 계산 예시 포함.",
        "documents": [
            {
                "filename": "tuition_and_refund.pdf",
                "file_type": "pdf",
                "content": """[등록/분납]
- 고지: 학기 시작 전 2주, 분납 2~3회 가능(연체이자 없음)
[환불]
- 개강 전: 전액, 개강 후 30일 이내: 5/6 반환, 60일 이내: 2/3, 90일 이내: 1/2
[감면]
- 다자녀/국가유공자/교직원 자녀/형편곤란 등 요건 충족 시 신청""",
            }
        ],
    },
    {
        "name": "교직원 행정 비서",
        "description": "회의실/차량 예약, 공문/품의서 양식, 출장·교육 신청, 증명서 발급",
        "model_name": "gpt-4o",
        "system_prompt": "내부결재 라인, 증빙서류, 기한을 체크리스트로 제시.",
        "documents": [
            {
                "filename": "admin_staff_hdbk.pdf",
                "file_type": "pdf",
                "content": """[결재/문서]
- 기안 → 팀장 → 실장 → 처장 순 결재(부서별 차이 가능)
- 품의서: 목적/예산/기간/성과 지표 명시
[출장]
- 사전결재, 영수증/교통비 정산, 보고서 제출 7일 이내
[회의실/차량]
- 포털 예약, 사용 후 정리 상태 사진 업로드""",
            }
        ],
    },
    {
        "name": "보건·상담 센터",
        "description": "건강검진, 예방접종, 심리상담, 학업/진로 스트레스 관리",
        "model_name": "gpt-4o",
        "system_prompt": "민감 정보는 익명과 개인정보 보호를 우선. 긴급상황시 119/캠퍼스 보안 연락.",
        "documents": [
            {
                "filename": "health_counseling_guide.pdf",
                "file_type": "pdf",
                "content": """[보건]
- 일반진료 평일 10:00~17:00(점심 12:00~13:00)
- 무료 예방접종 캠페인(독감/간염 시즌제)
[상담]
- 개인/집단 상담, 초기상담 후 배정
- 위기대응: 자해 위험 시 즉시 응급연락 체계 가동""",
            }
        ],
    },
    {
        "name": "주차·교통 안내",
        "description": "주차 등록/요금, 교내 셔틀 시간표, 대중교통 환승 팁",
        "model_name": "gpt-4o",
        "system_prompt": "혼잡 시간대, 대체 주차, 장애인·임산부 배려석 정보를 제공.",
        "documents": [
            {
                "filename": "parking_transport.pdf",
                "file_type": "pdf",
                "content": """[주차]
- 등록: 학번/사번, 차량번호, 보험증빙
- 요금: 월정액(학생 2만원, 교직원 3만원), 일일권 3천원
- 대체주차: 만차 시 외부 제휴주차장 2곳
[셔틀]
- 순환 10분 간격(08:20~18:00), 방학 중 20분""",
            }
        ],
    },
    {
        "name": "꿀교양·인기교양 추천",
        "description": "수강신청 성공률을 높이는 인기 교양 목록, 학점 잘 나오는 꿀교양 리스트, 강의평가 기반 추천 과목",
        "model_name": "gpt-4o",
        "system_prompt": "과도한 경쟁을 피하는 전략, 숨겨진 명강의(꿀교양) 발굴 팁, 전공 연계 추천 교양 정보를 제공.",
        "documents": [
            {
                "filename": "easy_electives_list.pdf",
                "file_type": "pdf",
                "content": """[추천 교양 리스트]
심리학개론 : 비대면 수업 3학점
우주의 역사 : 비대면 수업 3학점
운동방법의 실제 : 부담없이 들을 수 있는 실습 위주 수업 2학점
볼링 : 볼링을 좋아하는 학우라면 부담없이 들을 수 있음 2학점""",
            }
        ],
    },
]


def seed(db):
    try:
        # idempotent 시드를 위해 documents → chatbots 순으로 비움
        # (원하지 않으면 아래 두 줄 주석)
        db.query(Document).delete()
        db.query(Chatbot).delete()
        db.commit()

        inserted = 0
        for item in SEED:
            bot = Chatbot(
                name=item["name"],
                description=item["description"],
                model_name=item["model_name"],
                system_prompt=item["system_prompt"],
            )
            db.add(bot)
            db.flush()  # bot.id 확보
            for doc in item.get("documents", []):
                db.add(
                    Document(
                        filename=doc["filename"],
                        file_path="",  # 파일 경로 미사용
                        file_type=doc.get("file_type", "pdf"),
                        content=doc["content"],
                        chatbot_id=bot.id,
                    )
                )
            inserted += 1
        db.commit()
        print(
            f"✅ chatbots: {inserted}개, documents: {db.query(Document).count()}개 삽입 완료"
        )
    finally:
        db.close()
