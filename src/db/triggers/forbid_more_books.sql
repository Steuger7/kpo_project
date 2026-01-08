CREATE OR REPLACE FUNCTION forbid_more_books () RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
  book_number INTEGER := 1000;
BEGIN
  IF ( (SELECT u.book_count FROM collection_entry ce JOIN users u ON ce.collection_id = u.id AND NEW.collection_id = ce.collection_id) >= book_number) THEN
    RAISE EXCEPTION 'Cant add more books';
  END IF;

  RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER forbid_more_than_n_books BEFORE INSERT ON collection_entry FOR EACH ROW EXECUTE FUNCTION forbid_more_books();
