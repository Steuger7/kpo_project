import { expect, jest, test, describe, beforeEach } from "@jest/globals";
import { DatabaseController } from "../../db/db_controller.js";

describe("DatabaseController", () => {
  let mockPool;
  let dbController;
  let mockClient;

  beforeEach(() => {
    mockPool = {
      query: jest.fn(),
      connect: jest.fn(),
    };
    mockClient = {
      query: jest.fn(),
      release: jest.fn(),
    };
    dbController = new DatabaseController(mockPool);
  });

  describe("constructor", () => {
    test("should throw error when dbPool is null or undefined", () => {
      expect(() => new DatabaseController(null)).toThrow(
        "Null or undefined argument in DB controller construction",
      );
      expect(() => new DatabaseController(undefined)).toThrow(
        "Null or undefined argument in DB controller construction",
      );
    });
  });

  describe("getUser", () => {
    test("should query database with hashed credentials", async () => {
      const mockResult = { rows: [{ id: 1 }] };
      mockPool.query.mockResolvedValue(mockResult);

      const result = await dbController.getUser("username", "password");
      expect(mockPool.query).toHaveBeenCalled();
      expect(result).toBe(mockResult);
    });
  });

  describe("getUserBooks", () => {
    test("should query user books with correct parameters", async () => {
      const mockResult = { rows: [{ title: "Book 1" }] };
      mockPool.query.mockResolvedValue(mockResult);

      const result = await dbController.getUserBooks(123, "password", "");
      expect(mockPool.query).toHaveBeenCalled();
      expect(result).toBe(mockResult);
    });
  });

  describe("addUser", () => {
    test("should insert new user with hashed credentials", async () => {
      const mockResult = { rows: [{ id: 5 }] };
      mockPool.query.mockResolvedValue(mockResult);

      const result = await dbController.addUser("newuser", "newpass");
      expect(mockPool.query).toHaveBeenCalled();
      expect(result).toBe(mockResult);
    });
  });

  describe("deleteUser", () => {
    test("should delete user with hashed credentials", async () => {
      const mockResult = { rowCount: 1 };
      mockPool.query.mockResolvedValue(mockResult);

      const result = await dbController.deleteUser(123, "user", "pass");
      expect(mockPool.query).toHaveBeenCalled();
      expect(result).toBe(mockResult);
    });
  });

  describe("appendBook", () => {
    test("should call stored procedure with correct parameters", async () => {
      const mockResult = { rows: [] };
      mockPool.connect.mockResolvedValue(mockClient);
      mockClient.query.mockResolvedValue(mockResult);

      const result = await dbController.appendBook(
        123,
        "pass",
        456,
        2020,
        "key123",
        ["en"],
        "Book Title",
        ["JA manal"],
      );

      expect(mockPool.connect).toHaveBeenCalled();
      expect(mockClient.query).toHaveBeenCalled();
      expect(result).toBe(mockResult);
      expect(mockClient.release).toHaveBeenCalled();
    });

    test("should release client even when query throws", async () => {
      const mockClient = {
        query: jest.fn().mockRejectedValue(new Error("Query failed")),
        release: jest.fn(),
      };
      mockPool.connect.mockResolvedValue(mockClient);

      await expect(
        dbController.appendBook(
          123,
          "pass",
          456,
          2020,
          "key123",
          ["en"],
          "Title",
          ["JA manal"],
        ),
      ).rejects.toThrow("Query failed");
      expect(mockClient.release).toHaveBeenCalled();
    });
  });

  describe("deleteBook", () => {
    test("should call stored procedure to remove book", async () => {
      const mockResult = { rows: [] };
      mockPool.connect.mockResolvedValue(mockClient);
      mockClient.query.mockResolvedValue(mockResult);

      const result = await dbController.deleteBook(123, "pass", "book_key");

      expect(mockClient.query).toHaveBeenCalledWith(
        "CALL remove_book($1, $2, $3)",
        [123, "pass", "book_key"],
      );
      expect(result).toBe(mockResult);
    });
  });
});
