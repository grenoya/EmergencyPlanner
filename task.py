#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Task and Planning classes """
from datetime import datetime, timedelta, date, time

# Codes des couleurs
BLACK = "0m"
RED = "31m"
GREEN = "32m"
YELLOW = "33m"
BLUE = "34m"
MAGENTA = "35m"
CYAN = "36m"

# Codes des modes d'affichage
RESET = "\033[0;0m"
NORMAL = "\033[0;"
BOLD = "\033[1;"
REVERSE = "\033[7;"


class Task(object):
    """ Task class """
    def __init__(self, title="New Task", desc="", domain=None,
                 deadLine=datetime.max, estimate=timedelta(0)):
        #: Name of the Task
        self.title = title
        #: Description of the Task
        self.description = desc
        #: Task domain to which the Task belong
        self.domain = domain
        #: Deadline of the Task
        self.deadLine = deadLine
        #: Estimation of the full duration of the Task (timedelta)
        self.estimatedLength = estimate
        #: Percent of the work already done
        self.percentDone = 0
        #: lasting duration of the Task
        self.lastingTime = timedelta(0)
        #: Priority of the Task (calculated from the remaining duration and the deadline)
        self.priority = 0
        #: Startdate in the planning
        self.startdate = datetime.max
        #: Enddate in the planning
        self.enddate = self.deadLine
        #: Indicates that there is time (a pause) between this task and the next one
        self.pause = False

        self.updateLastingTime()
        self.updatePriority()

    def updatePercent(self, newPercent):
        """ Update *percentDone* with *newPercent* and update calculated attributs """
        if not 0 <= newPercent <= 100:
                raise ValueError("New percent should be between 0 and 100!")
                return
        self.percentDone = newPercent
        self.updateLastingTime()
        self.updatePriority()

    def updateLastingTime(self):
        """ Recompute the lasting duration of the task from percentDone """
        self.lastingTime = self.estimatedLength * (100 - self.percentDone) / 100

    def updatePriority(self):
        """ Recompute priority from current remaining duration and distance to deadline """
        T = self.deadLine - datetime.today()
        D = self.lastingTime
        if T >= D:
            P = D / T
        elif timedelta(0) < T < D:
            P = D / T
        else:
            P = (D - T) / D
        self.priority = P

    def __lt__(self, other):
        if self.deadLine == other.deadLine:
            if self.priority == other.priority:
                return self.title < other.title
            else:
                return self.priority > other.priority
        else:
            return self.deadLine < other.deadLine

    def __repr__(self):
        msg = "%s: %s (%s | %s | %s | P %.2f)" % (self.title, self.description,
                                                  self.deadLine, self.lastingTime,
                                                  self.domain, self.priority)
        return msg

    def __str__(self):
        msg = "[%s] %-15s : %s -> %s (%s | P %.2f)" % (self.domain[:3],
                                                       self.title[:15],
                                                       self.startdate.strftime("%m-%d %H:%M"),
                                                       self.enddate.strftime("%m-%d %H:%M"),
                                                       self.deadLine.strftime("%m-%d %H:%M"),
                                                       self.priority)
        if self.pause:
            msg += " *"
        return msg


class Holidays(object):
    """ Holidays class """
    def __init__(self, cal, title="New Holidays",
                 startday=date.max, starttime="AM",
                 endday=date.max, endtime="PM"):
        #: Name of the Task
        self.title = title
        # compute start date from startday and Calendar
        indday = startday.weekday()
        if starttime not in ("AM", "PM"):
            raise ValueError('starttime should be either "AM" or "PM"!')
        elif starttime == "AM":
            #: Startdate in the planning
            self.startdate = datetime.combine(startday,
                                              cal.periodes.starttime[indday*2])
        else:
            #: Startdate in the planning
            self.startdate = datetime.combine(startday,
                                              cal.periodes.starttime[indday*2+1])
        # compute end date from startday and Calendar
        indday = endday.weekday()
        if endtime not in ("AM", "PM"):
            raise ValueError('endtime should be either "AM" or "PM"!')
        elif endtime == "AM":
            #: Enddate in the planning
            self.enddate = datetime.combine(endday,
                                            cal.periodes.endtime[indday*2])
        else:
            #: Enddate in the planning
            self.enddate = datetime.combine(endday,
                                            cal.periodes.endtime[indday*2+1])
        #: Deadline of the Task
        self.deadLine = self.enddate

    def __lt__(self, other):
        if self.deadLine == other.deadLine:
            return self.title < other.title
        else:
            return self.deadLine < other.deadLine

    def __repr__(self):
        msg = "%s: %s -> %s" % (self.title, self.startdate, self.enddate)
        return msg

    def __str__(self):
        msg = "[CONG] %-15s : %s -> %s" % (self.title[:15],
                                           self.startdate.strftime("%m-%d %H:%M"),
                                           self.enddate.strftime("%m-%d %H:%M"))
        return msg


class WorkPeriode(object):
    """ Work periodes class """
    def __init__(self, wday, starttime, endtime, dt_prev):
        self.wday = wday
        self.starttime = starttime
        self.endtime = endtime
        self.dt_prev = timedelta(hours=dt_prev)

    def is_in_peride(self, dt, verbose=False):
        """ Tell if *dt* belong to this periode """
        _DAYS = ['LU', 'MA', 'ME', 'JE', 'VE', 'SA', 'DI']
        ret = False
        if verbose:
            print(dt, _DAYS[dt.weekday()])
            print("%s : %s --> %s" % (_DAYS[self.wday], self.starttime, self.endtime))
        if self.wday == dt.weekday() and \
            self.starttime <= dt.time() <= self.endtime:
            ret = True
        if verbose:
            print(ret)
        return ret


class Calendar(object):
    """ Calendar class """
    def __init__(self):
        # self.periodes = [WorkPeriode(0, time(9), time(12), 64), # Lu mat
        #                  WorkPeriode(0, time(13, 30), time(17, 30), 1.5), # Lu ap
        #                  WorkPeriode(1, time(9), time(12), 13), # Ma mat
        #                  WorkPeriode(1, time(13, 30), time(18), 1.5), # Ma ap
        #                  WorkPeriode(2, time(9), time(12), 13), # Me mat
        #                  WorkPeriode(2, time(13, 30), time(18), 1.5), # Me ap
        #                  WorkPeriode(3, time(9), time(12), 15), # Je mat
        #                  WorkPeriode(3, time(13, 30), time(19), 1.5), # Je ap
        #                  WorkPeriode(4, time(9), time(12), 14), # Ve mat
        #                  WorkPeriode(4, time(13, 30), time(17), 1.5), # Ve ap
        #                 ]
        self.periodes = [WorkPeriode(0, time(9), time(12), 64), # Lu mat
                         WorkPeriode(0, time(13, 00), time(18), 1), # Lu ap
                         WorkPeriode(1, time(9), time(12), 15), # Ma mat
                         WorkPeriode(1, time(14, 00), time(18), 2), # Ma ap
                         WorkPeriode(2, time(9), time(12), 15), # Me mat
                         WorkPeriode(2, time(13, 00), time(18), 1), # Me ap
                         WorkPeriode(3, time(9), time(12), 15), # Je mat
                         WorkPeriode(3, time(13, 00), time(19), 1), # Je ap
                         WorkPeriode(4, time(9), time(12), 14), # Ve mat
                         WorkPeriode(4, time(13, 00), time(17), 1), # Ve ap
                        ]
        self.num = len(self.periodes)
        self.current = 0

    def compute_startdate(self, end, duration):
        """ Compute start time of a task taking into account work hours """
        # initialize the start date at the end date
        start = end
        # In which periode are we?
        ret = False
        for i, per in enumerate(self.periodes):
            ret = per.is_in_peride(start, verbose=False)
            if ret:
                self.current = i
                break
        if not ret:
            print(start)
            raise ValueError("Please make sure the due date is a work day!")

        while duration > timedelta(0):
            remainingtime = start - datetime.combine(start.date(),
                                                     self.periodes[self.current].starttime)
            if remainingtime > duration:
                # there is enough time in this periode
                start -= duration
                duration = timedelta(0)
            else:
                # remove the remaining time from duration
                duration -= remainingtime
                # move to end of previous periode
                start -= remainingtime
                if duration != timedelta(0):
                    start -= self.periodes[self.current].dt_prev
                self.current -= 1
                self.current = self.current % self.num
        return start


class Planning(object):
    """ Planning class """
    def __init__(self, domains):
        #: Dictionary that will contain a list of tasks per domain
        self.tasks = {key:[] for key in domains}
        #: list of holidays
        self.holidays = []
        #: reference calendar
        self.cal = Calendar()

    def addTask(self, title="New Task", desc="", domain=None,
                 deadLine=datetime.max, estimate=timedelta(0)):
        if domain not in self.tasks:
            self.tasks[domain] = []
        task = Task(title=title, desc=desc, domain=domain,
                     deadLine=deadLine, estimate=estimate)
        self.tasks[domain].append(task)

    def updateTask(self, taskname, domain, newPercent):
        if not taskname in self.tasks[domain]:
            print("Task %s doesn't exist in %s" % (taskname, domain))
        ind = self.tasks[domain].index(taskname)
        self.tasks[domain][ind].updatePercent(newPercent)

    def addHolidays(self, title="New Holidays",
                    startday=date.max, starttime="AM",
                    endday=date.max, endtime="PM"):
        holday = Holidays(self.cal, title=title,
                     startday=date.max, starttime="AM",
                     endday=date.max, endtime="PM")
        self.holidays.append(holday)

    def count(self):
        cnt = 0
        for dom in self.tasks.values():
            cnt += len(dom)
        return cnt

    def count_domain(self, domain):
        cnt = timedelta(0)
        for ts in self.tasks[domain]:
            cnt += ts.lastingTime
        return cnt.total_seconds() / 3600

    def render_planning(self):
        """ Render the tasks as a Gantt-like chart """
        # Sort tasks on due dates and priority
        full_list = []
        for dom in self.tasks:
            self.tasks[dom].sort()
            full_list += self.tasks[dom]
        full_list.sort()

        # Compute tasks' start date backward
        full_list.reverse()
        final_list = []
        start_tmp = datetime.max
        for task in full_list:
            if task.deadLine == datetime.max:
                continue
            task.enddate = min(task.deadLine, start_tmp)
            if task.deadLine < start_tmp:
                task.pause = True
            # print(task.title)
            try:
                task.startdate = self.cal.compute_startdate(task.enddate,
                                                            task.lastingTime)
            except ValueError as err:
                print("%s : %s" % (task.title, err))
                break
            start_tmp = task.startdate
            final_list.insert(0, task)
        else:
            # Render planning
            msg = ""
            now = datetime.now()
            today = date.today()
            tomorrow = today + timedelta(days=1)
            tomorrow = datetime.combine(tomorrow, time(0))
            sat = today + timedelta(days=5-today.weekday())
            sat = datetime.combine(sat, time(0))
            for task in final_list:
                col = BLACK
                mod = NORMAL
                if task.deadLine < now:
                    mod = REVERSE
                    col = RED
                elif task.priority >= 1:
                    mod = BOLD
                    col = RED
                elif task.deadLine < tomorrow:
                    mod = BOLD
                    col = YELLOW
                elif task.deadLine < sat:
                    col = GREEN
                msg += mod + col + "%s\n" % str(task)
                msg += RESET + ""
            print(msg)

    def sort_priority(self, domain=None):
        """ Sort tasks for all domains and returns 6h of prioritary work """
        if domain:
            self.tasks[domain].sort(reverse=True)
            full_list = self.tasks[domain]
        else:
            full_list = []
            for dom in self.tasks:
                self.tasks[dom].sort()
                full_list += self.tasks[dom]
            full_list.sort()

        # render full_list
        if domain:
            print("For domain: %s" % domain)
            msg = "Sorted %3d priorities (%5.1f h):\n" % (len(full_list),
                                                          self.count_domain(domain))
            msg += "===============================\n"
        else:
            msg = "Sorted %3d priorities:\n" % self.count()
            msg += "=====================\n"
        for elem in full_list:
            msg += "%s\n" % elem
        print(msg)

        if not domain:
            # Totals per Domain
            msg = "\nTotal time per domain:\n"
            msg += "---------------------\n"
            for elem in self.tasks:
                msg += "%s: %5.1f h\n" % (elem, self.count_domain(elem))
            print(msg)

        # List True Emergencies
        msg = "\nEMERGENCIES:\n"
        msg += "-----------\n"
        for elem in full_list:
            if elem.priority > 1:
                msg += "%s\n" % elem
        print(msg)

        today = date.today()

        # Due by the end of the week
        msg = "\nDue by the end of the week:\n"
        msg += "--------------------------\n"
        sat = today + timedelta(days=5-today.weekday())
        sat = datetime.combine(sat, time(0))
        for elem in full_list:
            if elem.deadLine < sat:
                msg += "%s\n" % elem
        print(msg)
        # List due today
        msg = "\nDue today:\n"
        msg += "---------\n"
        tomorrow = today + timedelta(days=1)
        tomorrow = datetime.combine(tomorrow, time(0))
        for elem in full_list:
            if elem.deadLine < tomorrow:
                msg += "%s\n" % elem
        print(msg)

        # list of task to do in the next 6 hours
        short_list = []
        # cumulative time of the most prioritary tasks (in hours)
        total_time = 0
        # remaining time today
        remainingTime = (datetime.combine(date.today(), time(18)) - \
            datetime.now()).total_seconds() / 3600
        while total_time < remainingTime and len(full_list) > 0:
            short_list.append(full_list.pop(0))
            total_time += short_list[-1].lastingTime.total_seconds() / 3600
        msg = "\nShort list to do today:\n"
        msg += "======================\n"
        for elem in short_list:
            msg += "%s\n" % elem
        print(msg)
