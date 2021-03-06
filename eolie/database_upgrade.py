# Copyright (c) 2014-2018 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from eolie.sqlcursor import SqlCursor
from eolie.define import Type


class DatabaseUpgrade:
    """
        Manage database schema upgrades
    """

    def __init__(self, t):
        """
            Init object
            @param t as Type
        """
        # Here are schema upgrade, key is database version,
        # value is sql request
        if t == Type.BOOKMARK:
            self.__UPGRADES = {
                1: self.__upgrade_bookmarks_1,
                2: "ALTER TABLE bookmarks ADD startup INT NOT NULL DEFAULT 0",
            }
        elif t == Type.HISTORY:
            self.__UPGRADES = {
                1: "ALTER TABLE history ADD opened INT NOT NULL DEFAULT 0",
                2: "ALTER TABLE history ADD netloc TEXT NOT NULL DEFAULT ''",
                3: "DELETE FROM history WHERE popularity=0",
                4: "DELETE FROM history_atime WHERE NOT EXISTS (SELECT * FROM\
                    history WHERE history.rowid=history_atime.history_id)",
                5: "CREATE INDEX idx_orderby ON history(mtime, popularity)",
                6: "CREATE INDEX idx_where ON history(uri, title)"
            }
        elif t == Type.SETTINGS:
            self.__UPGRADES = {
                1: "ALTER TABLE settings ADD audio INT NOT NULL DEFAULT 1",
            }

    def upgrade(self, db):
        """
            Upgrade db
            @param db as Database
        """
        version = 0
        with SqlCursor(db) as sql:
            result = sql.execute("PRAGMA user_version")
            v = result.fetchone()
            if v is not None:
                version = v[0]
            if version < self.version:
                for i in range(version + 1, self.version + 1):
                    try:
                        if isinstance(self.__UPGRADES[i], str):
                            sql.execute(self.__UPGRADES[i])
                        else:
                            self.__UPGRADES[i](db)
                    except Exception as e:
                        print("DatabaseUpgrade %s failed: %s" % (i, e))
                sql.execute("PRAGMA user_version=%s" % self.version)

    @property
    def version(self):
        """
            Current wanted version
        """
        return len(self.__UPGRADES)

#######################
# PRIVATE             #
#######################
    def __upgrade_bookmarks_1(self, db):
        """
            Remove del column
            @param db as BookmarksDatabase
        """
        create_bookmarks = '''CREATE TABLE bookmarks (
                                           id INTEGER PRIMARY KEY,
                                           title TEXT NOT NULL,
                                           uri TEXT NOT NULL,
                                           popularity INT NOT NULL,
                                           atime REAL NOT NULL,
                                           guid TEXT NOT NULL,
                                           mtime REAL NOT NULL,
                                           position INT DEFAULT 0
                                           )'''
        with SqlCursor(db) as sql:
            sql.execute("ALTER TABLE bookmarks RENAME TO _bookmarks")
            sql.execute(create_bookmarks)
            sql.execute("""INSERT INTO bookmarks (id, title, uri,
                            popularity, atime, guid, mtime, position)
                           SELECT id, title, uri, popularity, atime, guid,
                            mtime, position FROM _bookmarks""")
            sql.execute("DROP TABLE _bookmarks")
