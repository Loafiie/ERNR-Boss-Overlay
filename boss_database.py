import sqlite3

# Maximum allowed Levenshtein distance as a fraction of the DB name length.
# e.g. 0.45 means the OCR text must be within 45% edits of a boss name.
MAX_DISTANCE_RATIO = 0.45

# Boss names listed here are exceptions: when multiple rows share this name
# (or one name is a prefix of another), show only the entry with the highest ID.
# All other duplicate names show all entities side-by-side (val1 / val2).
SINGLE_ENTITY_OVERRIDES = {
    "Gnoster Wisdom of Night",
}


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

    def _row_to_entity(self, row):
        """Convert a DB row into an entity stats dict."""
        return {
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
        }

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
                from logger import log
                log(f"         ↳ DB reject: '{cleaned_name}' ≠ '{best_row[1]}' "
                    f"(dist={best_dist}, ratio={best_ratio:.0%})")
                return None

            # Gather ALL rows whose name matches (or starts with) the best match
            matched_name = best_row[1]
            matching_rows = [
                r for r in self._bosses
                if r[1] == matched_name or r[1].startswith(matched_name)
            ]

            # Check if this boss is a single-entity override:
            # show only the entry with the highest ID
            is_override = any(
                matched_name.lower().startswith(ov.lower())
                for ov in SINGLE_ENTITY_OVERRIDES
            )

            if is_override and len(matching_rows) > 1:
                best = max(matching_rows, key=lambda r: r[0])
                matching_rows = [best]
                # Update best_row to the override target
                best_row = best

            entities = [self._row_to_entity(r) for r in matching_rows]

            return {
                "id": best_row[0],
                "boss_name": matched_name,
                "entities": entities,
                "distance": best_dist,
                "ocr_input": cleaned_name,
            }

        except Exception as e:
            from logger import log
            log(f"         ↳ DB error for '{boss_name}': {e}")
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