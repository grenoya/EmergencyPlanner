#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Task and Planning classes """
from datetime import datetime, timedelta, date, time


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
        if self.priority == other.priority:
            return self.title < other.title
        else:
            return self.priority < other.priority

    def __repr__(self):
        msg = "%s: %s (%s | P %.2f)" % (self.title, self.description,
                                      self.lastingTime, self.priority)
        return msg


class Planning(object):
    """ Planning class """
    def __init__(self, domains):
        #: Dictionary that will contain a list of tasks per domain
        self.tasks = {key:[] for key in domains}

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

    def sort(self):
        """ Sort tasks for all domains and returns 6h of prioritary work """
        full_list = []
        for domain in self.tasks:
            self.tasks[domain].sort(reverse=True)
            full_list += self.tasks[domain]

        full_list.sort(reverse=True)
        msg = "Sorted %3d priorities:\n" % self.count()
        msg += "=====================\n"
        for elem in full_list:
            msg += "%s\n" % elem
        print(msg)
        # list of task to do in the next 6 hours
        short_list = []
        # cumulative time of the most prioritary tasks (in hours)
        total_time = 0
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
        return msg

    def sort_domain(self, domain):
        """ Sort tasks for 1 domain and returns 6h of prioritary work """
        self.tasks[domain].sort(reverse=True)
        full_list = self.tasks[domain]
        print("For domain: %s" % domain)
        msg = "Sorted %3d priorities (%5.1f h):\n" % (len(full_list),
                                                      self.count_domain(domain))
        msg += "===============================\n"
        for elem in full_list:
            msg += "%s\n" % elem
        print(msg)

        # list of task to do in the next 6 hours
        short_list = []
        # cumulative time of the most prioritary tasks (in hours)
        total_time = 0

        # List True Emergencies
        msg = "\nEMERGENCIES:\n"
        msg += "-----------\n"
        for elem in full_list:
            if elem.priority > 1:
                msg += "%s\n" % elem
        print(msg)

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
        return msg
