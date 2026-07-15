const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000/api/v1";


export class ApiError extends Error {
  constructor(message, status, details = null) {
    super(message);

    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}


async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    return response.json();
  }

  return response.text();
}


async function request(url, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${url}`, options);
  } catch (error) {
    throw new ApiError(
      "백엔드 서버에 연결할 수 없습니다.",
      0,
      error
    );
  }

  const payload = await parseResponse(response);

  if (!response.ok) {
    const detail =
      payload && typeof payload === "object"
        ? payload.detail
        : null;

    const message =
      detail?.message ||
      detail ||
      payload?.error?.message ||
      "API 요청에 실패했습니다.";

    throw new ApiError(
      message,
      response.status,
      payload
    );
  }

  return payload;
}


export async function createTranscription({
  file,
  useDiarization = true,
  speakerCount = null,
  removeDisfluency = true,
  splitParagraph = true,
  keywords = "",
}) {
  const formData = new FormData();

  formData.append("file", file);
  formData.append(
    "use_diarization",
    String(useDiarization)
  );
  formData.append(
    "remove_disfluency",
    String(removeDisfluency)
  );
  formData.append(
    "split_paragraph",
    String(splitParagraph)
  );

  if (speakerCount !== null && speakerCount !== "") {
    formData.append(
      "speaker_count",
      String(speakerCount)
    );
  }

  if (keywords.trim()) {
    formData.append(
      "keywords",
      keywords.trim()
    );
  }

  return request("/transcriptions", {
    method: "POST",
    body: formData,
  });
}


export async function getTranscriptionStatus(jobId) {
  return request(`/transcriptions/${jobId}`);
}


export async function getTranscriptionResult(jobId) {
  return request(`/transcriptions/${jobId}/result`);
}


export async function downloadMarkdown(jobId) {
  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/transcriptions/${jobId}/markdown`
    );
  } catch (error) {
    throw new ApiError(
      "백엔드 서버에 연결할 수 없습니다.",
      0,
      error
    );
  }

  if (!response.ok) {
    const payload = await parseResponse(response);

    const message =
      payload?.detail?.message ||
      payload?.detail ||
      "Markdown 다운로드에 실패했습니다.";

    throw new ApiError(
      message,
      response.status,
      payload
    );
  }

  const blob = await response.blob();

  const disposition =
    response.headers.get("content-disposition") || "";

  const utf8Match = disposition.match(
    /filename\*=UTF-8''([^;]+)/
  );

  const basicMatch = disposition.match(
    /filename="([^"]+)"/
  );

  const fileName = utf8Match
    ? decodeURIComponent(utf8Match[1])
    : basicMatch?.[1] || "meeting_minutes.md";

  const downloadUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");

  anchor.href = downloadUrl;
  anchor.download = fileName;

  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();

  URL.revokeObjectURL(downloadUrl);
}