import sqlite3
import unittest


class FtsVocabularyTests(unittest.TestCase):
    def test_column_document_frequency(self):
        conn = sqlite3.connect(":memory:")
        try:
            conn.execute("CREATE VIRTUAL TABLE search USING fts5(country,src,nname,naddr)")
            conn.execute("INSERT INTO search VALUES (?,?,?,?)", ("US", "s2", "acme bakery", "12 market road"))
            conn.execute("INSERT INTO search VALUES (?,?,?,?)", ("US", "s3", "acme foods", "54 river road"))
            conn.execute("CREATE VIRTUAL TABLE vocab USING fts5vocab(search, 'col')")
            self.assertEqual(conn.execute("SELECT doc FROM vocab WHERE term='acme' AND col='nname'").fetchone(), (2,))
            self.assertEqual(conn.execute("SELECT doc FROM vocab WHERE term='market' AND col='naddr'").fetchone(), (1,))
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
