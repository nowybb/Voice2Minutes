import { useRef, useState } from "react";
import Header from "./components/Header";

const SUPPORTED_FORMATS = [
  "audio/mpeg",
  "audio/mp4",
  "audio/x-m4a",
  "audio/wav",
  "audio/flac",
  "video/mp4",
];

function formatFileSize(bytes) {
  if (!bytes) return "";

  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    units.length - 1
  );

  const size = bytes / 1024 ** index;

  return `${size.toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

function App() {
  const fileInputRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const validateFile = (file) => {
    if (!file) return;

    const extension = file.name.split(".").pop()?.toLowerCase();
    const allowedExtensions = ["mp3", "m4a", "mp4", "wav", "flac", "amr"];

    const validType =
      SUPPORTED_FORMATS.includes(file.type) ||
      allowedExtensions.includes(extension);

    if (!validType) {
      setSelectedFile(null);
      setErrorMessage(
        "지원하지 않는 파일 형식입니다. MP3, M4A, MP4, WAV, FLAC, AMR 파일을 선택해 주세요."
      );
      return;
    }

    const maxSize = 2 * 1024 * 1024 * 1024;

    if (file.size > maxSize) {
      setSelectedFile(null);
      setErrorMessage("파일 크기는 2GB 이하여야 합니다.");
      return;
    }

    setErrorMessage("");
    setSelectedFile(file);
  };

  const handleFileChange = (event) => {
    validateFile(event.target.files?.[0]);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);

    validateFile(event.dataTransfer.files?.[0]);
  };

  const removeFile = () => {
    setSelectedFile(null);
    setErrorMessage("");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleGenerate = () => {
    if (!selectedFile) {
      setErrorMessage("먼저 회의 음성 파일을 선택해 주세요.");
      return;
    }

    alert(
      `${selectedFile.name} 파일이 선택되었습니다.\n다음 단계에서 RTZR STT API를 연결합니다.`
    );
  };

  return (
    <div className="app">
      <Header />

      <main>
        <section className="hero-section">
          <div className="container hero-container">
            <div className="hero-copy">
              <p className="hero-label">AI MEETING ASSISTANT</p>

              <h1>
                회의 음성을
                <br />
                <span>실행 가능한 회의록</span>으로
              </h1>

              <p className="hero-description">
                음성 파일을 업로드하면 전사부터 핵심 요약, 결정 사항,
                실행 항목까지 한 번에 정리합니다.
              </p>

              <div className="hero-tags">
                <span>RTZR STT</span>
                <span>Speaker Diarization</span>
                <span>Meeting Summary</span>
              </div>
            </div>

            <div className="upload-wrapper" id="upload">
              <div className="upload-heading">
                <div>
                  <p className="upload-step">01</p>
                  <h2>회의 음성 업로드</h2>
                </div>

                <span className="upload-status">
                  {selectedFile ? "준비 완료" : "파일 대기 중"}
                </span>
              </div>

              {!selectedFile ? (
                <button
                  type="button"
                  className={`drop-zone ${isDragging ? "dragging" : ""}`}
                  onClick={() => fileInputRef.current?.click()}
                  onDragOver={(event) => {
                    event.preventDefault();
                    setIsDragging(true);
                  }}
                  onDragLeave={() => setIsDragging(false)}
                  onDrop={handleDrop}
                >
                  <span className="wave-icon" aria-hidden="true">
                    <i />
                    <i />
                    <i />
                    <i />
                    <i />
                  </span>

                  <strong>회의 음성 파일을 올려주세요.</strong>

                  <span>
                    파일을 끌어 놓거나 클릭하여 선택할 수 있습니다.
                  </span>
                </button>
              ) : (
                <div className="selected-file">
                  <div className="selected-file-icon">
                    <span className="wave-icon small" aria-hidden="true">
                      <i />
                      <i />
                      <i />
                      <i />
                      <i />
                    </span>
                  </div>

                  <div className="selected-file-info">
                    <strong>{selectedFile.name}</strong>
                    <span>{formatFileSize(selectedFile.size)}</span>
                  </div>

                  <button
                    type="button"
                    className="remove-file-button"
                    onClick={removeFile}
                    aria-label="선택한 파일 제거"
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
                  <input type="checkbox" defaultChecked />
                  <span>화자 분리</span>
                </label>

                <label>
                  <input type="checkbox" defaultChecked />
                  <span>간투어 제거</span>
                </label>

                <label>
                  <input type="checkbox" defaultChecked />
                  <span>문단 나누기</span>
                </label>
              </div>

              {errorMessage && (
                <p className="upload-error">{errorMessage}</p>
              )}

              <button
                type="button"
                className="generate-button"
                disabled={!selectedFile}
                onClick={handleGenerate}
              >
                회의록 생성하기
                <span aria-hidden="true">→</span>
              </button>

              <p className="upload-guide">
                MP3, M4A, MP4, WAV, FLAC, AMR · 최대 2GB
              </p>
            </div>
          </div>

          <div className="hero-pattern" aria-hidden="true" />
        </section>

        <section className="value-section">
          <div className="container value-grid">
            <article>
              <span>01</span>
              <h3>빠른 전사</h3>
              <p>긴 회의 음성을 RTZR STT로 빠르게 텍스트로 변환합니다.</p>
            </article>

            <article>
              <span>02</span>
              <h3>구조화된 회의록</h3>
              <p>핵심 요약, 결정 사항과 실행 항목을 구분해 보여줍니다.</p>
            </article>

            <article>
              <span>03</span>
              <h3>바로 활용</h3>
              <p>생성된 결과를 Markdown 회의록으로 저장할 수 있습니다.</p>
            </article>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;