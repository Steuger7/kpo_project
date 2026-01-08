import { expect, jest, test, describe, beforeEach } from "@jest/globals";
import { AppController } from "../../search_controller.js";

global.fetch = jest.fn();

describe("AppController", () => {
  let mockDbController;
  let appController;

  beforeEach(() => {
    mockDbController = {
      getUserBooks: jest.fn(),
      appendBook: jest.fn(),
      deleteBook: jest.fn(),
    };
    appController = new AppController(mockDbController);
    fetch.mockClear();
  });

  describe("constructor", () => {
    test("should throw error when dbController is null or undefined", () => {
      expect(() => new AppController(null)).toThrow(
        "Null or undefined argument in AppContoller construction",
      );
      expect(() => new AppController(undefined)).toThrow(
        "Null or undefined argument in AppContoller construction",
      );
    });
  });

  describe("getSavedBooks", () => {
    test("should get books from database", async () => {
      const mockBooks = [
        { id: 1, title: "Book 1" },
        { id: 2, title: "Book 2" },
      ];
      const mockResponse = { rows: mockBooks };
      mockDbController.getUserBooks.mockResolvedValue(mockResponse);

      const result = await appController.getSavedBooks(123, "password", "");
      expect(mockDbController.getUserBooks).toHaveBeenCalledWith(
        123,
        "password",
        "",
      );
      expect(result).toEqual(mockBooks);
    });

    test("should return empty array when no books found", async () => {
      const mockResponse = { rows: [] };
      mockDbController.getUserBooks.mockResolvedValue(mockResponse);

      const result = await appController.getSavedBooks(123, "password", "");
      expect(result).toEqual([]);
    });
  });

  describe("saveBook", () => {
    test("should save book via database controller", async () => {
      mockDbController.appendBook.mockResolvedValue({});

      await appController.saveBook(
        123,
        "pass",
        456,
        2020,
        "key123",
        ["en"],
        "Title",
        ["JA manal"],
      );
      expect(mockDbController.appendBook).toHaveBeenCalledWith(
        123,
        "pass",
        456,
        2020,
        "key123",
        ["en"],
        "Title",
        ["JA manal"],
      );
    });
  });

  describe("deleteBook", () => {
    test("should delete book via database controller", async () => {
      mockDbController.deleteBook.mockResolvedValue({});

      await appController.deleteBook(123, "pass", "book_key");
      expect(mockDbController.deleteBook).toHaveBeenCalledWith(
        123,
        "pass",
        "book_key",
      );
    });
  });
});
