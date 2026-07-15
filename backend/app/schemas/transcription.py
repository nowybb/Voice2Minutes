from typing import Optional

from pydantic import BaseModel, Field


class TranscriptionOptions(BaseModel):
    use_diarization: bool = Field(
        default=True,
        description="화자 분리 사용 여부"
    )

    speaker_count: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
        description="예상 화자 수"
    )

    remove_disfluency: bool = Field(
        default=True,
        description="간투어 제거"
    )

    split_paragraph: bool = Field(
        default=True,
        description="문단 자동 분리"
    )

    keywords: Optional[str] = Field(
        default=None,
        description="쉼표(,)로 구분한 키워드"
    )