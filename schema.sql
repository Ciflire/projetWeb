CREATE TABLE IF NOT EXISTS "users" (
        "name"  TEXT NOT NULL UNIQUE,
        "admin" INTEGER NOT NULL,
        "hash"  TEXT NOT NULL,
        "profile_picture"       INTEGER,
        PRIMARY KEY("id_user" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "challenges" (
        "id_challenge"  INTEGER NOT NULL UNIQUE,
        "name"  TEXT NOT NULL,
        "creation_date" INTEGER NOT NULL,
        "end_date"      INTEGER,
        PRIMARY KEY("id_challenge" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "validations" (
        "id_user"       INTEGER NOT NULL,
        "id_challenge"  INTEGER NOT NULL,
        "inscription_date"      INTEGER NOT NULL,
        "validation_date"       INTEGER,
        "token" TEXT NOT NULL,
        FOREIGN KEY("id_challenge") REFERENCES "challenges"("id_challenge"),
        FOREIGN KEY("id_user") REFERENCES "users"("id_user"),
        PRIMARY KEY("id_user","id_challenge")
);
/* No STAT tables available */

