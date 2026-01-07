import { assert } from "./assert.js";

export class AppController {
  constructor(dbController) {
    if (!dbController) {
      throw Error("Null or undefined argument in AppContoller construction");
    }
    this.db = dbController;
  }

  async getSavedBooks(userid, password, query) {
    let dbResponse = await this.db.getUserBooks(userid, password, query);
    return dbResponse.rows;
  }

  async saveBook(userid, password, cover, fyp, key, lang, title, author_name) {
    await this.db.appendBook(
      userid,
      password,
      cover,
      fyp,
      key,
      lang,
      title,
      author_name,
    );
  }

  async deleteBook(userid, password, key) {
    await this.db.deleteBook(userid, password, key);
  }
}
