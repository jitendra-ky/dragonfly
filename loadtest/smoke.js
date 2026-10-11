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
  vus: 2,
  duration: "30s",
  thresholds: {
    http_req_duration: ["p(95)<500"],
    http_req_failed: ["rate<0.01"],
    checks: ["rate>0.99"],
  },
};

function jsonParams(token) {
  return {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  };
}

function namedParams(token, name) {
  return { ...jsonParams(token), tags: { name } };
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
    "login returns access token": (r) => Boolean(r.json("access")),
    "login returns user id": (r) => Number(r.json("user.id")) > 0,
  });
  if (response.status !== 200 || !response.json("access")) {
    throw new Error(`Login failed: ${response.status} ${response.body}`);
  }
  return { token: response.json("access"), userId: Number(response.json("user.id")) };
}

export default function (data) {
  const params = jsonParams(data.token);
  let response = http.get(`${baseUrl}/api/health/`, { tags: { name: "health" } });
  endpointTrends.health.add(response.timings.duration);
  check(response, {
    "health status is 200": (r) => r.status === 200,
    "health response is healthy": (r) => r.json("status") === "healthy",
  });
  sleep(0.2);

  response = http.get(`${baseUrl}/api/all-users/`, namedParams(data.token, "all-users"));
  endpointTrends.allUsers.add(response.timings.duration);
  check(response, {
    "all users status is 200": (r) => r.status === 200,
    "all users response is an array": (r) => Array.isArray(r.json()),
  });
  const users = response.json();
  const receiver = users.find((user) => user.id !== data.userId);
  check(response, { "peer user is available": () => Boolean(receiver) });
  sleep(0.3);

  response = http.get(`${baseUrl}/api/contacts/`, namedParams(data.token, "contacts"));
  endpointTrends.contacts.add(response.timings.duration);
  check(response, {
    "contacts status is 200": (r) => r.status === 200,
    "contacts response is an array": (r) => Array.isArray(r.json()),
  });
  sleep(0.3);

  if (receiver) {
    response = http.get(`${baseUrl}/api/messages/`, {
      ...params,
      headers: { ...params.headers, receiver: String(receiver.id) },
      tags: { name: "messages-read" },
    });
    endpointTrends.messagesRead.add(response.timings.duration);
    check(response, {
      "messages status is 200": (r) => r.status === 200,
      "messages response is an array": (r) => Array.isArray(r.json()),
    });
    sleep(0.3);

    response = http.post(
      `${baseUrl}/api/messages/`,
      JSON.stringify({ receiver: receiver.id, content: `smoke-${__VU}-${__ITER}` }),
      { ...params, tags: { name: "messages-write" } },
    );
    endpointTrends.messagesWrite.add(response.timings.duration);
    check(response, {
      "send message status is 201": (r) => r.status === 201,
      "sent message has id": (r) => Number(r.json("id")) > 0,
      "sent message has content": (r) => r.json("content") !== undefined,
    });
  }
  sleep(0.5);
}
