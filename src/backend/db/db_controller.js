import { assert } from "../assert.js";

export class DatabaseController {
  constructor(dbPool) {
    if (!dbPool) {
      throw Error("Null or undefined argument in DB controller construction");
    }
    this.db = dbPool;
  }

  async getUser(username, password) {
    return await this.db.query(
      "SELECT id FROM users WHERE username = hash_string($1) AND password = hash_string($2)",
      [username, password],
    );
  }

  async getUserBooks(userid, password, search_query) {
    let q = "";
    if (search_query != "") {
      q = search_query + "|" + search_query.replaceAll(" ", "|");
    }
    return await this.db.query(
      String.raw`select ce.cover_i, ce.first_publish_year, ce.key, ce.language, ce.title from collection_entry ce LEFT JOIN users u ON u.id = ce.collection_id WHERE ce.collection_id=$1 AND u.password=hash_string($2) AND ce.title ~* $3 ORDER BY
      (CASE
        WHEN title ILIKE $4 THEN 1
        WHEN title ILIKE $4 THEN 2
        WHEN title ILIKE $4 THEN 3
        ELSE 4
      END),
      title`,
      [userid, password, q, search_query],
    );
  }

  async appendBook(
    userid,
    password,
    cover_i,
    fyp,
    key,
    lang,
    title,
    first_publish_year,
  ) {
    const client = await this.db.connect();
    let response;
    try {
      response = client.query(
        "CALL append_book($1, $2, $3, $4, $5, $6, $7, $8)",
        [userid, password, cover_i, fyp, key, lang, title, first_publish_year],
      );
    } finally {
      client.release();
    }
    return response;
  }

  async addUser(username, password) {
    return await this.db.query(
      "INSERT INTO users (username, password) values (hash_string($1), hash_string($2)) RETURNING id",
      [username, password],
    );
  }

  async deleteUser(userid, username, password) {
    return await this.db.query(
      "DELETE FROM users WHERE id = $1 AND username = hash_string($2) AND password = hash_string($3)",
      [userid, username, password],
    );
  }

  async deleteBook(userid, password, key) {
    const client = await this.db.connect();
    let response;
    try {
      response = client.query("CALL remove_book($1, $2, $3)", [
        userid,
        password,
        key,
      ]);
    } finally {
      client.release();
    }
    return response;
  }
}
