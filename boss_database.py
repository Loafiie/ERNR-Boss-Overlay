import sqlite3

# Maximum allowed Levenshtein distance as a fraction of the DB name length.
# e.g. 0.45 means the OCR text must be within 45% edits of a boss name.
MAX_DISTANCE_RATIO = 0.45


class BossDatabase:
    def __init__(self, db_name):
        self.db_name = db_name
        # Cache all boss rows once at startup
        self._bosses = self._load_bosses()

    def _load_bosses(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT * FROM T_bosses")
        rows = cur.fetchall()
        con.close()
        return rows

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
        try:
            cleaned_name = boss_name.strip()
            input_name = cleaned_name.lower().replace(" ", "")

            if len(input_name) < 3:
                return None

            best_row = None
            best_ratio = float("inf")
            best_dist = 0

            for row in self._bosses:
                db_norm = row[1].lower().replace(" ", "")
                db_len = len(db_norm)
                if db_len == 0:
                    continue

                # Full-string distance
                d_full = self.levenshtein(input_name, db_norm)

                # Also try prefix: truncate OCR text to DB name length
                # Handles trailing garbage like 'DemiHumanQueensey'
                d = d_full
                if len(input_name) > db_len:
                    prefix = input_name[:db_len]
                    d_prefix = self.levenshtein(prefix, db_norm)
                    d = min(d_full, d_prefix)

                # Compare by ratio so short names don't win unfairly
                ratio = d / db_len
                if ratio < best_ratio:
                    best_ratio = ratio
                    best_row = row
                    best_dist = d

            if best_row is None:
                return None

            if best_ratio > MAX_DISTANCE_RATIO:
                print(f"         ↳ DB reject: '{cleaned_name}' ≠ '{best_row[1]}' "
                      f"(dist={best_dist}, ratio={best_ratio:.0%})")
                return None

            return {
                "id": best_row[0],
                "boss_name": best_row[1],
                "standard": best_row[2],
                "slash": best_row[3],
                "strike": best_row[4],
                "pierce": best_row[5],
                "magic": best_row[6],
                "fire": best_row[7],
                "lightning": best_row[8],
                "holy": best_row[9],
                "poison": best_row[10],
                "scarlet_rot": best_row[11],
                "blood_loss": best_row[12],
                "frostbite": best_row[13],
                "sleep": best_row[14],
                "madness": best_row[15],
                "distance": best_dist,
                "ocr_input": cleaned_name,
            }

        except Exception as e:
            print(f"         ↳ DB error for '{boss_name}': {e}")
            return None

    def find_best_matches(self, boss_name_array):
        results = []
        seen_boss_ids = set()

        for boss_name in boss_name_array:
            match = self.find_best_match(boss_name)
            if match is not None:
                if match["id"] in seen_boss_ids:
                    continue
                seen_boss_ids.add(match["id"])
                results.append(match)

        return results