import http from "k6/http";
import { Trend } from "k6/metrics";
import { check, sleep } from "k6";

const baseUrl = __ENV.BASE_URL || "http://web:8000";
const email = __ENV.LOADTEST_EMAIL || "loadtest-0000@example.com";
const password = __ENV.LOADTEST_PASSWORD || "LoadtestPassword123!";
const endpointTrends = {
  signIn: new Trend("endpoint_sign_in"),
  health: new Trend("endpoint_health"),
  allUsers: new Trend("endpoint_all_users"),
  contacts: new Trend("endpoint_contacts"),
  messagesRead: new Trend("endpoint_messages_read"),
  messagesWrite: new Trend("endpoint_messages_write"),
};

export const options = {
  stages: [
    { duration: "30s", target: 10 },
    { duration: "30s", target: 30 },
    { duration: "2m", target: 30 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"],
    http_req_failed: ["rate<0.01"],
    checks: ["rate>0.99"],
  },
};

function authParams(token, receiver, name) {
  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
  if (receiver) headers.receiver = String(receiver);
  return { headers, tags: { name } };
}

export function setup() {
  const response = http.post(
    `${baseUrl}/api/sign-in/`,
    JSON.stringify({ email, password }),
    { headers: { "Content-Type": "application/json" }, tags: { name: "sign-in" } },
  );
  endpointTrends.signIn.add(response.timings.duration);
  check(response, {
    "login status is 200": (r) => r.status === 200,
    "login response has access token": (r) => Boolean(r.json("access")),
  });
  if (response.status !== 200 || !response.json("access")) {
    throw new Error(`Login failed: ${response.status} ${response.body}`);
  }
  const token = response.json("access");
  const userId = Number(response.json("user.id"));
  const usersResponse = http.get(
    `${baseUrl}/api/all-users/`,
    authParams(token, undefined, "all-users-setup"),
  );
  endpointTrends.allUsers.add(usersResponse.timings.duration);
  check(usersResponse, {
    "setup users status is 200": (r) => r.status === 200,
    "setup users response is an array": (r) => Array.isArray(r.json()),
  });
  const receiver = usersResponse.json().find((user) => user.id !== userId);
  if (!receiver) throw new Error("No seeded peer user found");
  return { token, receiverId: receiver.id };
}

export default function (data) {
  const token = data.token;
  const receiverId = data.receiverId;

  let response = http.get(`${baseUrl}/api/health/`, { tags: { name: "health" } });
  endpointTrends.health.add(response.timings.duration);
  check(response, {
    "health status is 200": (r) => r.status === 200,
    "health response shape is valid": (r) => r.json("status") === "healthy",
  });
  sleep(0.2);

  response = http.get(`${baseUrl}/api/contacts/`, authParams(token, undefined, "contacts"));
  endpointTrends.contacts.add(response.timings.duration);
  check(response, {
    "contacts status is 200": (r) => r.status === 200,
    "contacts response shape is valid": (r) => Array.isArray(r.json()),
  });
  sleep(0.3);

  response = http.get(`${baseUrl}/api/all-users/`, authParams(token, undefined, "all-users"));
  endpointTrends.allUsers.add(response.timings.duration);
  check(response, {
    "all users status is 200": (r) => r.status === 200,
    "all users response shape is valid": (r) => Array.isArray(r.json()),
  });
  sleep(0.4);

  response = http.get(
    `${baseUrl}/api/messages/`,
    authParams(token, receiverId, "messages-read"),
  );
  endpointTrends.messagesRead.add(response.timings.duration);
  check(response, {
    "messages status is 200": (r) => r.status === 200,
    "messages response shape is valid": (r) => Array.isArray(r.json()),
  });
  sleep(0.4);

  response = http.post(
    `${baseUrl}/api/messages/`,
    JSON.stringify({
      receiver: receiverId,
      content: `load-${__VU}-${__ITER}`,
    }),
    authParams(token, undefined, "messages-write"),
  );
  endpointTrends.messagesWrite.add(response.timings.duration);
  check(response, {
    "send message status is 201": (r) => r.status === 201,
    "send response has id": (r) => Number(r.json("id")) > 0,
    "send response has receiver": (r) => Number(r.json("receiver")) === receiverId,
  });
  sleep(0.5);
}
