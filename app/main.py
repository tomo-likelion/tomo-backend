from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.email_analyses import router as email_analyses_router
from app.api.routes.recipients import router as recipients_router

app = FastAPI(
    title="TOMO API",
    description=(
        "수신자의 문화적 배경과 관계를 고려해 이메일의 위험 요소를 분석하고 "
        "더 적절한 표현을 추천하는 TOMO 백엔드 API입니다."
    ),
    version="0.1.0",
    openapi_tags=[
        {
            "name": "상태 확인",
            "description": "서버가 정상적으로 요청을 처리할 수 있는지 확인합니다.",
        },
        {
            "name": "수신자 관리",
            "description": "이메일 분석에 사용할 수신자 프로필을 등록하고 조회합니다.",
        },
        {
            "name": "이메일 분석",
            "description": "이메일을 분석하고 문화적 위험 요소와 개선안을 제공합니다.",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(recipients_router)
app.include_router(email_analyses_router)


@app.get(
    "/health",
    tags=["상태 확인"],
    summary="서버 상태 확인",
    description="서버 프로세스가 실행 중이며 요청에 응답할 수 있는지 확인합니다.",
    response_description="서버의 현재 상태",
)
def health_check():
    return {
        "status": "ok"
    }
