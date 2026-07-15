import { useEffect, useRef, useState } from "react";

import Header from "./components/Header";
import {
  createTranscription,
  downloadMarkdown,
  getTranscriptionResult,
  getTranscriptionStatus,
} from "./services/api";

const SUPPORTED_FORMATS = [
  "audio/mpeg",
  "audio/mp4",
  "audio/x-m4a",
  "audio/wav",
  "audio/flac",
  "video/mp4",
];

const ALLOWED_EXTENSIONS = [
  "mp3",
  "m4a",
  "mp4",
  "wav",
  "flac",
  "amr",
];

const MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024;
const POLLING_INTERVAL = 2000;

function formatFileSize(bytes) {
  if (!bytes) {
    return "";
  }

  const units = ["B", "KB", "MB", "GB"];

  const index = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    units.length - 1
  );

  const size = bytes / 1024 ** index;

  return `${size.toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

function formatTimestamp(milliseconds) {
  const totalSeconds = Math.max(
    0,
    Math.floor(milliseconds / 1000)
  );

  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor(
    (totalSeconds % 3600) / 60
  );
  const seconds = totalSeconds % 60;

  if (hours > 0) {
    return [
      hours,
      minutes,
      seconds,
    ]
      .map((value) => String(value).padStart(2, "0"))
      .join(":");
  }

  return [minutes, seconds]
    .map((value) => String(value).padStart(2, "0"))
    .join(":");
}

function App() {
  const fileInputRef = useRef(null);
  const pollingTimerRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  const [useDiarization, setUseDiarization] =
    useState(true);
  const [removeDisfluency, setRemoveDisfluency] =
    useState(true);
  const [splitParagraph, setSplitParagraph] =
    useState(true);

  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState("idle");
  const [progress, setProgress] = useState(null);
  const [meetingResult, setMeetingResult] =
    useState(null);

  const [errorMessage, setErrorMessage] =
    useState("");
  const [isDownloading, setIsDownloading] =
    useState(false);

  const isProcessing = [
    "uploading",
    "queued",
    "transcribing",
    "summarizing",
  ].includes(jobStatus);

  useEffect(() => {
    return () => {
      if (pollingTimerRef.current) {
        clearTimeout(pollingTimerRef.current);
      }
    };
  }, []);

  const validateFile = (file) => {
    if (!file) {
      return;
    }

    const extension = file.name
      .split(".")
      .pop()
      ?.toLowerCase();

    const validType =
      SUPPORTED_FORMATS.includes(file.type) ||
      ALLOWED_EXTENSIONS.includes(extension);

    if (!validType) {
      setSelectedFile(null);
      setErrorMessage(
        "지원하지 않는 파일 형식입니다. MP3, M4A, MP4, WAV, FLAC, AMR 파일을 선택해 주세요."
      );
      return;
    }

    if (file.size === 0) {
      setSelectedFile(null);
      setErrorMessage(
        "빈 파일은 업로드할 수 없습니다."
      );
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setSelectedFile(null);
      setErrorMessage(
        "파일 크기는 2GB 이하여야 합니다."
      );
      return;
    }

    resetJobState();

    setErrorMessage("");
    setSelectedFile(file);
  };

  const resetJobState = () => {
    if (pollingTimerRef.current) {
      clearTimeout(pollingTimerRef.current);
      pollingTimerRef.current = null;
    }

    setJobId(null);
    setJobStatus("idle");
    setProgress(null);
    setMeetingResult(null);
  };

  const handleFileChange = (event) => {
    validateFile(event.target.files?.[0]);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);

    validateFile(
      event.dataTransfer.files?.[0]
    );
  };

  const removeFile = () => {
    resetJobState();

    setSelectedFile(null);
    setErrorMessage("");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const fetchCompletedResult = async (
    currentJobId
  ) => {
    const response =
      await getTranscriptionResult(
        currentJobId
      );

    setMeetingResult(response.data);
    setJobStatus("completed");
    setProgress({
      step: 4,
      total_steps: 4,
      label: "회의록 생성이 완료되었습니다.",
    });

    window.setTimeout(() => {
      document
        .getElementById("result")
        ?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
    }, 100);
  };

  const pollJobStatus = async (
    currentJobId
  ) => {
    try {
      const response =
        await getTranscriptionStatus(
          currentJobId
        );

      const statusData = response.data;
      const currentStatus =
        statusData.status;

      setJobStatus(currentStatus);
      setProgress(statusData.progress);

      if (currentStatus === "completed") {
        await fetchCompletedResult(
          currentJobId
        );
        return;
      }

      if (currentStatus === "failed") {
        const message =
          statusData.error?.message ||
          "회의록 생성에 실패했습니다.";

        setErrorMessage(message);
        return;
      }

      pollingTimerRef.current =
        window.setTimeout(
          () => {
            pollJobStatus(currentJobId);
          },
          POLLING_INTERVAL
        );
    } catch (error) {
      setJobStatus("failed");
      setErrorMessage(
        error.message ||
          "작업 상태를 확인하지 못했습니다."
      );
    }
  };

  const handleGoHome = () => {
  resetJobState();

  setSelectedFile(null);
  setErrorMessage("");
  setIsDragging(false);

  setUseDiarization(true);
  setRemoveDisfluency(true);
  setSplitParagraph(true);

  if (fileInputRef.current) {
    fileInputRef.current.value = "";
  }

  window.history.replaceState(
    null,
    "",
    window.location.pathname
  );

  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });
};

  const handleGenerate = async () => {
    if (!selectedFile) {
      setErrorMessage(
        "먼저 회의 음성 파일을 선택해 주세요."
      );
      return;
    }

    if (isProcessing) {
      return;
    }

    resetJobState();
    setErrorMessage("");
    setJobStatus("uploading");

    setProgress({
      step: 1,
      total_steps: 4,
      label: "음성 파일을 업로드하고 있습니다.",
    });

    try {
      const response =
        await createTranscription({
          file: selectedFile,
          useDiarization,
          removeDisfluency,
          splitParagraph,
        });

      const createdJob = response.data;

      setJobId(createdJob.job_id);
      setJobStatus(createdJob.status);
      setProgress({
        step: 1,
        total_steps: 4,
        label:
          "전사 작업을 준비하고 있습니다.",
      });

      await pollJobStatus(
        createdJob.job_id
      );
    } catch (error) {
      setJobStatus("failed");
      setErrorMessage(
        error.message ||
          "파일 업로드에 실패했습니다."
      );
    }
  };

  const handleMarkdownDownload =
    async () => {
      if (!jobId || isDownloading) {
        return;
      }

      setIsDownloading(true);
      setErrorMessage("");

      try {
        await downloadMarkdown(jobId);
      } catch (error) {
        setErrorMessage(
          error.message ||
            "Markdown 다운로드에 실패했습니다."
        );
      } finally {
        setIsDownloading(false);
      }
    };

  const getUploadStatusText = () => {
    if (jobStatus === "uploading") {
      return "업로드 중";
    }

    if (jobStatus === "queued") {
      return "작업 대기 중";
    }

    if (jobStatus === "transcribing") {
      return "전사 중";
    }

    if (jobStatus === "summarizing") {
      return "회의록 생성 중";
    }

    if (jobStatus === "completed") {
      return "생성 완료";
    }

    if (jobStatus === "failed") {
      return "처리 실패";
    }

    if (selectedFile) {
      return "준비 완료";
    }

    return "파일 대기 중";
  };

  return (
    <div className="app">
      <Header onLogoClick={handleGoHome} />

      <main>
        <section className="hero-section">
          <div className="container hero-container">
            <div className="hero-copy">
              <p className="hero-label">
                AI MEETING ASSISTANT
              </p>

              <h1>
                회의 음성을
                <br />
                <span>
                  실행 가능한 회의록
                </span>
                으로
              </h1>

              <p className="hero-description">
                회의 음성을 업로드하면 전사부터 요약, 실행 항목까지 자동으로 완성합니다.
              </p>

              <div className="hero-tags">
                <span>RTZR STT</span>
                <span>
                  Speaker Diarization
                </span>
                <span>Meeting Summary</span>
              </div>
            </div>

            <div
              className="upload-wrapper"
              id="upload"
            >
              <div className="upload-heading">
                <div>
                  <p className="upload-step">
                    
                  </p>

                  <h2>회의 음성 업로드</h2>
                </div>

                <span className="upload-status">
                  {getUploadStatusText()}
                </span>
              </div>

              {!selectedFile ? (
                <button
                  type="button"
                  className={
                    `drop-zone ${
                      isDragging
                        ? "dragging"
                        : ""
                    }`
                  }
                  onClick={() =>
                    fileInputRef.current?.click()
                  }
                  onDragOver={(event) => {
                    event.preventDefault();
                    setIsDragging(true);
                  }}
                  onDragLeave={() =>
                    setIsDragging(false)
                  }
                  onDrop={handleDrop}
                  disabled={isProcessing}
                >
                  <span
                    className="wave-icon"
                    aria-hidden="true"
                  >
                    <i />
                    <i />
                    <i />
                    <i />
                    <i />
                  </span>

                  <strong>
                    회의 음성 파일을
                    올려주세요.
                  </strong>

                  <span>
                    파일을 끌어 놓거나
                    클릭하여 선택할 수
                    있습니다.
                  </span>
                </button>
              ) : (
                <div className="selected-file">
                  <div className="selected-file-icon">
                    <span
                      className="wave-icon small"
                      aria-hidden="true"
                    >
                      <i />
                      <i />
                      <i />
                      <i />
                      <i />
                    </span>
                  </div>

                  <div className="selected-file-info">
                    <strong>
                      {selectedFile.name}
                    </strong>

                    <span>
                      {formatFileSize(
                        selectedFile.size
                      )}
                    </span>
                  </div>

                  <button
                    type="button"
                    className="remove-file-button"
                    onClick={removeFile}
                    aria-label="선택한 파일 제거"
                    disabled={isProcessing}
                  >
                    ×
                  </button>
                </div>
              )}

              <input
                ref={fileInputRef}
                type="file"
                hidden
                accept=".mp3,.m4a,.mp4,.wav,.flac,.amr"
                onChange={handleFileChange}
              />

              <div className="upload-options">
                <label>
                  <input
                    type="checkbox"
                    checked={useDiarization}
                    onChange={(event) =>
                      setUseDiarization(
                        event.target.checked
                      )
                    }
                    disabled={isProcessing}
                  />

                  <span>화자 분리</span>
                </label>

                <label>
                  <input
                    type="checkbox"
                    checked={removeDisfluency}
                    onChange={(event) =>
                      setRemoveDisfluency(
                        event.target.checked
                      )
                    }
                    disabled={isProcessing}
                  />

                  <span>간투어 제거</span>
                </label>

                <label>
                  <input
                    type="checkbox"
                    checked={splitParagraph}
                    onChange={(event) =>
                      setSplitParagraph(
                        event.target.checked
                      )
                    }
                    disabled={isProcessing}
                  />

                  <span>문단 나누기</span>
                </label>
              </div>

              {progress && (
                <div className="processing-status">
                  <div className="processing-status-header">
                    <span>
                      {progress.label}
                    </span>

                    <strong>
                      {progress.step}/
                      {progress.total_steps}
                    </strong>
                  </div>

                  <div className="progress-track">
                    <span
                      style={{
                        width: `${
                          (
                            progress.step /
                            progress.total_steps
                          ) * 100
                        }%`,
                      }}
                    />
                  </div>
                </div>
              )}

              {errorMessage && (
                <p className="upload-error">
                  {errorMessage}
                </p>
              )}

              <button
  type="button"
  className="generate-button"
  disabled={
    isProcessing ||
    (!selectedFile && jobStatus !== "completed")
  }
  onClick={
    jobStatus === "completed"
      ? handleMarkdownDownload
      : handleGenerate
  }
>
  {jobStatus === "completed"
    ? isDownloading
      ? "다운로드 중..."
      : "Markdown 다운로드"
    : isProcessing
      ? "회의록 생성 중..."
      : "회의록 생성하기"}

  <span aria-hidden="true">
    {jobStatus === "completed" ? "↓" : "→"}
  </span>
</button>

              <p className="upload-guide">
                MP3, M4A, MP4, WAV, FLAC,
                AMR · 최대 2GB
              </p>
            </div>
          </div>

          <div
            className="hero-pattern"
            aria-hidden="true"
          />
        </section>

        {meetingResult && (
          <section
            className="result-section"
            id="result"
          >
            <div className="container">
              <div className="result-heading">
                <div>
                  <p className="hero-label">
                    MEETING MINUTES
                  </p>

                  <h2>생성된 회의록</h2>

                  <p>
                    {meetingResult.file?.name}
                  </p>
                </div>

                <button
                  type="button"
                  className="markdown-button"
                  onClick={
                    handleMarkdownDownload
                  }
                  disabled={isDownloading}
                >
                  {isDownloading
                    ? "다운로드 중..."
                    : "Markdown 다운로드"}
                </button>
              </div>

              <div className="result-grid">
                <article className="result-card summary-card">
                  <span className="result-number">
                    01
                  </span>

                  <h3>핵심 요약</h3>

                  <p>
                    {meetingResult.summary}
                  </p>
                </article>

                <article className="result-card">
                  <span className="result-number">
                    02
                  </span>

                  <h3>결정 사항</h3>

                  {meetingResult.decisions
                    ?.length > 0 ? (
                    <ul>
                      {meetingResult.decisions.map(
                        (decision) => (
                          <li key={decision.id}>
                            {decision.content}
                          </li>
                        )
                      )}
                    </ul>
                  ) : (
                    <p>
                      추출된 결정 사항이
                      없습니다.
                    </p>
                  )}
                </article>

                <article className="result-card">
                  <span className="result-number">
                    03
                  </span>

                  <h3>Action Items</h3>

                  {meetingResult.action_items
                    ?.length > 0 ? (
                    <ul>
                      {meetingResult.action_items.map(
                        (item) => (
                          <li key={item.id}>
                            {item.task}
                          </li>
                        )
                      )}
                    </ul>
                  ) : (
                    <p>
                      추출된 실행 항목이
                      없습니다.
                    </p>
                  )}
                </article>

                <article className="result-card">
                  <span className="result-number">
                    04
                  </span>

                  <h3>주요 키워드</h3>

                  <div className="result-keywords">
                    {meetingResult.keywords
                      ?.length > 0 ? (
                      meetingResult.keywords.map(
                        (keyword) => (
                          <span key={keyword}>
                            {keyword}
                          </span>
                        )
                      )
                    ) : (
                      <p>
                        추출된 키워드가
                        없습니다.
                      </p>
                    )}
                  </div>
                </article>
              </div>

              <article className="transcript-card">
                <div className="transcript-heading">
                  <div>
                    <span className="result-number">
                      05
                    </span>

                    <h3>전체 전사문</h3>
                  </div>

                  <span>
                    {
                      meetingResult.transcript
                        ?.utterances?.length
                    }
                    개 발화
                  </span>
                </div>

                <div className="transcript-list">
                  {meetingResult.transcript
                    ?.utterances?.map(
                    (utterance, index) => (
                      <div
                        className="transcript-item"
                        key={`${utterance.start_ms}-${index}`}
                      >
                        <div className="speaker-label">
                          <strong>
                            화자{" "}
                            {utterance.speaker}
                          </strong>

                          <span>
                            {formatTimestamp(
                              utterance.start_ms
                            )}
                          </span>
                        </div>

                        <p>{utterance.text}</p>
                      </div>
                    )
                  )}
                </div>
              </article>
            </div>
          </section>
        )}

        {!meetingResult && (
  <section
    className="features-section"
    id="features"
  >
    <div className="container">
      <div className="section-heading">
        <p className="hero-label">
          FEATURES
        </p>

        <h2>
          회의 정리를 더 빠르고
          <br />
          명확하게 만듭니다.
        </h2>

        <p>
          음성 전사부터 핵심 정리와 결과 저장까지,
          회의 후 필요한 기능을 한곳에 담았습니다.
        </p>
      </div>

      <div className="features-grid">
        <article className="feature-card">
          <span className="feature-number">
            01
          </span>

          <div className="feature-icon">
            〽
          </div>

          <h3>빠른 전사</h3>

          <p>
            긴 회의 음성을 RTZR STT로
            빠르게 텍스트로 변환합니다.
          </p>
        </article>

        <article className="feature-card">
          <span className="feature-number">
            02
          </span>

          <div className="feature-icon">
            ◉
          </div>

          <h3>화자 분리</h3>

          <p>
            발화자를 구분해 누가 어떤 내용을
            말했는지 쉽게 확인할 수 있습니다.
          </p>
        </article>

        <article className="feature-card">
          <span className="feature-number">
            03
          </span>

          <div className="feature-icon">
            ≡
          </div>

          <h3>구조화된 회의록</h3>

          <p>
            핵심 요약, 결정 사항과 실행 항목을
            구분하여 한눈에 보여줍니다.
          </p>
        </article>

        <article className="feature-card">
          <span className="feature-number">
            04
          </span>

          <div className="feature-icon">
            ↓
          </div>

          <h3>바로 활용</h3>

          <p>
            생성된 결과를 Markdown 회의록으로
            내려받아 바로 활용할 수 있습니다.
          </p>
        </article>
      </div>
    </div>
  </section>
)}
{!meetingResult && (
  <>
    <section
      className="process-section"
      id="how-it-works"
    >
      <div className="container">
        <div className="section-heading">
          <p className="hero-label">
            HOW IT WORKS
          </p>

          <h2>
            음성 파일 하나로
            <br />
            회의록이 완성됩니다.
          </h2>

          <p>
            업로드부터 전사, 내용 정리,
            다운로드까지 네 단계로 진행합니다.
          </p>
        </div>

        <div className="process-grid">
          <article className="process-card">
            <span className="process-number">
              01
            </span>

            <div className="process-icon">
              ↑
            </div>

            <h3>음성 업로드</h3>

            <p>
              회의 음성 파일을 선택하거나
              화면에 끌어 놓습니다.
            </p>
          </article>

          <article className="process-card">
            <span className="process-number">
              02
            </span>

            <div className="process-icon">
              〽
            </div>

            <h3>음성 전사</h3>

            <p>
              RTZR STT가 음성을 분석하고
              화자별 텍스트로 변환합니다.
            </p>
          </article>

          <article className="process-card">
            <span className="process-number">
              03
            </span>

            <div className="process-icon">
              ≡
            </div>

            <h3>회의록 정리</h3>

            <p>
              핵심 요약과 결정 사항,
              실행 항목을 구조화합니다.
            </p>
          </article>

          <article className="process-card">
            <span className="process-number">
              04
            </span>

            <div className="process-icon">
              ↓
            </div>

            <h3>결과 다운로드</h3>

            <p>
              생성된 회의록을 Markdown
              파일로 저장합니다.
            </p>
          </article>
        </div>
      </div>
    </section>

    <section
  className="preview-section"
  id="preview"
>
  <div className="container">
    <div className="section-heading">
      <p className="hero-label">
        PREVIEW
      </p>

      <h2>
        회의의 핵심을
        <br />
        한눈에 확인하세요.
      </h2>

      <p>
        긴 전사문을 전부 읽지 않아도 핵심 요약,
        결정 사항과 후속 업무를 빠르게 확인할 수 있습니다.
      </p>
    </div>

    <div className="preview-result-card">
      <div className="preview-result-header">
        <div>
          <span className="preview-label">
            MEETING MINUTES
          </span>

          <h3>7월 마케팅 전략 회의</h3>
        </div>

        <span className="preview-complete">
          생성 완료
        </span>
      </div>

      <div className="preview-result-grid">
        <article className="preview-result-item preview-summary-card">
          <span className="preview-item-number">
            01
          </span>

          <h4>핵심 요약</h4>

          <p>
            신제품 출시를 앞두고 SNS 캠페인과 광고 예산을 중심으로
마케팅 전략을 논의했습니다.
콘텐츠 제작 일정과 채널별 운영 방향을 확정하기로 했습니다.
          </p>
        </article>

        <article className="preview-result-item">
          <span className="preview-item-number">
            02
          </span>

          <h4>결정 사항</h4>

          <ul>
            <li>
              인스타그램과 유튜브를 핵심 홍보 채널로 운영합니다.
            </li>
            <li>
              광고 예산은 디지털 광고에 우선 배분합니다.
            </li>
          </ul>
        </article>

        <article className="preview-result-item">
          <span className="preview-item-number">
            03
          </span>

          <h4>Action Items</h4>

          <ul>
            <li>
              마케팅 콘텐츠 제작 일정을 이번 주까지 확정합니다.
            </li>
            <li>
              광고 소재 시안을 금요일까지 공유합니다.
            </li>
          </ul>
        </article>

        <article className="preview-result-item">
          <span className="preview-item-number">
            04
          </span>

          <h4>주요 키워드</h4>

          <div className="preview-keywords">
            <span>마케팅</span>
            <span>SNS</span>
            <span>광고</span>
            <span>콘텐츠</span>
          </div>
        </article>
      </div>
    </div>
  </div>
</section>
  </>
)}
      </main>
    </div>
  );
}

export default App;