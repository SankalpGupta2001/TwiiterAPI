const sqlite3 = require("sqlite3").verbose();

def create_tables():
    
    conn = sqlite3.connect("query.db"
    # create user table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1
        )
        """
    )

    # create twitter_profile table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS twitter_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bearer_token TEXT NOT NULL,
            consumer_key TEXT NOT NULL,
            consumer_secret TEXT NOT NULL,
            access_token TEXT NOT NULL,
            access_token_secret TEXT NOT NULL,
            is_connected BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )

    # create follower table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS follower (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            twitter_profile_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            screen_name TEXT NOT NULL,
            follower_count INTEGER NOT NULL,
            FOREIGN KEY (twitter_profile_id) REFERENCES twitter_profile (id)
        )
        """
    )

    conn.commit()
    conn.close()

