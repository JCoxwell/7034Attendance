import sqlite3
from datetime import datetime, date, time

class AttendanceDB:

    def __init__(self, db_name=None):
        self.db_name = db_name or 'attendance.db'
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        self._create_tables()

    def close(self):
        self.con.close()

    def _create_tables(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS students"
                         "(student_id INTEGER NOT NULL PRIMARY KEY, name, year, subteam)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS timecards"
                         "(student_id, time_in, time_out, hours)")

    def write_student(self, student_id, name, year, subteam):
        self.cur.execute("INSERT INTO students (student_id, name, year, subteam) VALUES (?, ?, ?, ?)",
                         (student_id, name, year, subteam))
        self.con.commit()

    def get_students(self):
        cur = self.con.cursor()
        res = cur.execute("SELECT * from students")
        return res.fetchall()

    def write_timecard(self, student_id, dt_in, dt_out):
        hours = (dt_out - dt_in).total_seconds()/(60*60)
        self.cur.execute("INSERT INTO timecards (student_id, time_in, time_out, hours) VALUES (?, ?, ?, ?)",
                         (student_id, dt_in.isoformat(), dt_out.isoformat(), hours))
        self.con.commit()

    def get_timecards(self, student_id):
        res = self.cur.execute("SELECT * from timecards where student_id = ?",
                               (student_id,))
        return res.fetchall()

    def clock_in(self, student_id):
        #TODO: check to see if student is already signed in
        time_in = datetime.now().isoformat()
        self.cur.execute("INSERT INTO timecards (student_id, time_in, time_out, hours) VALUES (?, ?, ?, ?)",
                    (student_id, time_in, None, None))
        self.con.commit()

    def clock_out(self, student_id):
        res = self.cur.execute("SELECT rowid, time_in from timecards where student_id = ? and time_out is null",
                               (student_id,))
        row = res.fetchall()
        if not row:
            raise Exception("Student not signed in.")
        rowid = row[0][0]
        time_in = datetime.fromisoformat(row[0][1])
        time_out = datetime.now()
        hours = (time_out - time_in).total_seconds()/(60*60)
        self.cur.execute("UPDATE timecards set time_out = ?, hours = ? where rowid = ?",
                         (time_out.isoformat(), hours, rowid))
        self.con.commit()
        return hours

    def get_total_hours(self, student_id):
        # COALESCE takes first non null value in the arg list
        # the purpose here is to return 0 if the student has no timecards
        res = self.cur.execute("SELECT COALESCE(sum(hours), 0) from timecards where student_id = ?",
                               (student_id,))
        rows = res.fetchall()
        return rows[0][0]

    def clock_out_all(self):
        # maybe run something like this every day after lob close to clock out students who forgot
        res = self.cur.execute("SELECT rowid, time_in from timecards where time_out is null")
        rows = res.fetchall()
        time_out = datetime.combine(date.today(), time(21, 0))
        for row in rows:
            rowid = row[0]
            time_in = datetime.fromisoformat(row[1])
            hours = (time_out - time_in).total_seconds()/(60*60)
            self.cur.execute("UPDATE timecards set time_out = ?, hours = ? where rowid = ?",
                             (time_out.isoformat(), hours, rowid))
        self.con.commit()
