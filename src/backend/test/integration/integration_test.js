import { assert } from "../../assert.js";

const host = process.env.HOST;

console.log("Trying to register");
const response = await fetch(host + "register", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    username: "s",
    password: "a",
  }),
}).then((response) => {
  return response.json();
});
console.log(response);
console.assert(response.success, "register");
console.log("");

console.log("Trying to login");
let response2 = await fetch(host + "login", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    username: "s",
    password: "a",
  }),
}).then((response) => {
  return response.json();
});
console.log(response2);
let user = Object(response2);
console.assert(response2.success, "login");
console.log("");

console.log("Trying to addbook");
response2 = await fetch(host + "lib/addbook", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    userid: user.userid,
    password: user.password,
    cover_i: 11,
    first_year_publish: 2004,
    key: "/works/OL8065988M",
    language: ["jpn", "krn"],
    title: "the lord of the rings",
  }),
}).then((response) => {
  return response.json();
});
console.log(response2);
console.assert(response2.success, "addbook");
console.log("");

console.log("Trying to addbook2");
response2 = await fetch(host + "lib/addbook", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    userid: user.userid,
    password: user.password,
    cover_i: 11,
    first_year_publish: 2004,
    key: "/works/OL8066000M",
    language: ["jpn", "krn"],
    title: "the lord of the rings",
  }),
}).then((response) => {
  return response.json();
});
console.log(response2);
console.assert(response2.success, "addbook2");
console.log("");

console.log("Trying to check lib");
response2 = await fetch(host + "lib", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    userid: user.userid,
    password: user.password,
    query: "",
  }),
}).then((response) => {
  return response.json();
});
console.log(response2);
console.assert(response2.success, "lib");
console.log("");

console.log("Trying to removebook");
response2 = await fetch(host + "lib/removebook", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    userid: user.userid,
    password: user.password,
    key: "/works/OL8065988M",
  }),
}).then((response) => {
  return response.json();
});
console.log(response2);
console.assert(response2.success, "removebook");
console.log("");

console.log("Trying to check lib after removing a book");
response2 = await fetch(host + "lib", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    userid: user.userid,
    password: user.password,
    query: "",
  }),
}).then((response) => {
  return response.json();
});
console.log(response2);
console.assert(response2.success, "lib2");
console.log("");

console.log("Trying to removebook2");
response2 = await fetch(host + "lib/removebook", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    userid: user.userid,
    password: user.password,
    key: "/works/OL8066000M",
  }),
}).then((response) => {
  return response.json();
});
console.log(response2);
console.assert(response2.success, "removebook2");
console.log("");

console.log("Trying to deleteuser");
let response3 = await fetch(host + "deleteuser", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    userid: user.userid,
    username: user.username,
    password: user.password,
  }),
}).then((response) => {
  return response.json();
});
console.log(response3);
assert(response2.success, "deleteuser");
console.log("");

console.log("TEST COMPLETED");
