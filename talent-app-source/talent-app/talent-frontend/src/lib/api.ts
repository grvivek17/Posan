const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(options?.headers || {}),
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

// Profiles
export async function uploadResume(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/api/profiles/upload", { method: "POST", body: formData });
}

export async function listProfiles() {
  return request("/api/profiles/");
}

export async function getProfile(id: number) {
  return request(`/api/profiles/${id}`);
}

export async function deleteProfile(id: number) {
  return request(`/api/profiles/${id}`, { method: "DELETE" });
}

// Talent Finder
export async function chatTalentFinder(message: string) {
  return request("/api/talent-finder/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
}

// Requirements
export async function listRequirements() {
  return request("/api/requirements/");
}

export async function createRequirement(data: {
  title: string;
  description?: string;
  skills_needed?: string;
  team_size?: number;
  status?: string;
}) {
  return request("/api/requirements/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function updateRequirement(
  id: number,
  data: {
    title?: string;
    description?: string;
    skills_needed?: string;
    team_size?: number;
    status?: string;
  }
) {
  return request(`/api/requirements/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function deleteRequirement(id: number) {
  return request(`/api/requirements/${id}`, { method: "DELETE" });
}

export async function matchProfilesForRequirement(id: number) {
  return request(`/api/requirements/${id}/match-profiles`);
}

// Telecaller
export async function listQuestions(requirementId?: number) {
  const query = requirementId ? `?requirement_id=${requirementId}` : "";
  return request(`/api/telecaller/questions${query}`);
}

export async function createQuestion(data: {
  requirement_id?: number;
  question: string;
  question_order?: number;
}) {
  return request("/api/telecaller/questions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function deleteQuestion(id: number) {
  return request(`/api/telecaller/questions/${id}`, { method: "DELETE" });
}

export async function createCall(data: {
  profile_id: number;
  requirement_id?: number;
}) {
  return request("/api/telecaller/calls", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function listCalls() {
  return request("/api/telecaller/calls");
}

export async function submitBulkResponses(data: {
  call_id: number;
  responses: { question_id: number; response: string }[];
}) {
  return request("/api/telecaller/responses/bulk", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

// Twilio
export async function getTwilioStatus() {
  return request("/api/telecaller/twilio-status");
}

export async function createTwilioCall(data: {
  profile_id: number;
  requirement_id?: number;
  phone_number: string;
}) {
  return request("/api/telecaller/calls/twilio", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function getCallStatus(callId: number) {
  return request(`/api/telecaller/calls/${callId}/status`);
}
