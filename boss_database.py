import sqlite3


class BossDatabase:
    def __init__(self, db_name):
        self.db_name = db_name

    @staticmethod
    def levenshtein(a, b):
        if len(a) < len(b):
            return BossDatabase.levenshtein(b, a)

        if len(b) == 0:
            return len(a)

        previous_row = range(len(b) + 1)
        for i, c1 in enumerate(a):
            current_row = [i + 1]
            for j, c2 in enumerate(b):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def find_best_match(self, boss_name):
        con = None

        try:
            cleaned_name = boss_name.strip()
            input_name = cleaned_name.lower().replace(" ", "")

            con = sqlite3.connect(self.db_name)
            con.create_function("levenshtein", 2, BossDatabase.levenshtein)
            cur = con.cursor()

            cur.execute("""
                SELECT *,
                       levenshtein(LOWER(REPLACE(F_BossName, ' ', '')), ?) AS dist
                FROM T_bosses
                ORDER BY dist ASC
                LIMIT 1;
            """, (input_name,))

            row = cur.fetchone()
            if not row:
                return None

            return {
                "id": row[0],
                "boss_name": row[1],
                "standard": row[2],
                "slash": row[3],
                "strike": row[4],
                "pierce": row[5],
                "magic": row[6],
                "fire": row[7],
                "lightning": row[8],
                "holy": row[9],
                "poison": row[10],
                "scarlet_rot": row[11],
                "blood_loss": row[12],
                "frostbite": row[13],
                "sleep": row[14],
                "madness": row[15],
                "distance": row[16],
                "ocr_input": cleaned_name,
            }

        except Exception as e:
            print(f"Database error for '{boss_name}': {e}")
            return None

        finally:
            if con:
                con.close()

    def find_best_matches(self, boss_name_array):
        results = []

        for boss_name in boss_name_array:
            match = self.find_best_match(boss_name)
            if match is not None:
                results.append(match)

        return results