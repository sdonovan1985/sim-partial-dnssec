import sys
import random

PRINTALL = False

class Server(object):
    def __init__(self):
        self.requests = 0
        self.false_reports = 0
        self.requests_since_last_false_report = 0

    def handle_request(self, request):
        raise NotImplementedError("Child class did not implement handle_request()")
    def log_false_request(self):
        self.false_reports += 1
        self._print_report("false")
        self.requests_since_last_false_report = 0

    def log_good_request(self):
        self.requests_since_last_false_report += 1
        self._print_report("good")

    def log_state(self):
        self._print_record()
        
    def _print_report(self, val=None):
        if PRINTALL == True or val == None:
            if val == None:
                print "%s status" % self__class__.__name__
            else:
                print "Creating %s request  - %s" % (val, self.__class__.__name__)
            print "    self.requests:       %d" % self.requests
            print "    self.false_reports:  %d" % self.false_reports
            print "    self.since_last:     %d" % self.requests_since_last_false_report

# Randomly, this server will return a bad value.
# percentage is an integer between 0 and 100. 
#    0 is always truthful, 100 is always lying
class RandomServer(Server):
    def __init__(self, percentage):
        super(RandomServer,self).__init__()
        self.percentage = percentage
        self.sysrand = random.SystemRandom()

    def handle_request(self, request):
        self.requests += 1
        randNum = self.sysrand.randint(1,100)
        if randNum <= self.percentage:
            self.log_false_request()
            return False
        self.log_good_request()
        return True

    def __str__(self):
        return ("%s:\n    percent:%d%%\n    requests: %i" % 
                (self.__class__.__name__ , 
                 self.percentage,
                 self.requests))
         


# For any domain in list hijackedDomains, return a bad value.
# hijackedDomains is a list of domains that server 'hijacks' and returns bad
# values for. Defaults to just domain 1.
class FixedServer(Server):
    def __init__(self, hijackedDomains=[1]):
        super(FixedServer,self).__init__()
        self.hijacks = hijackedDomains

    def handle_request(self, request):
        self.requests += 1
        if request in self.hijacks:
            self.log_false_request()
            return False
        self.log_good_request()
        return True

    def __str__(self):
        return ("%s:\n    domains:%s\n    requests: %i" % 
                (self.__class__.__name__ , 
                 str(self.hijacks),
                 self.requests))
         



class Client(object):
    def __init__(self, server, maxDomain):
        self.sysrand = random.SystemRandom()
        self.server = server
        self.maxDomain = maxDomain
        self.most_recent_request = None
        self.requests = 0
        self.unverified_valid_reports = 0
        self.unverified_invalid_reports = 0
        self.verified_valid_reports = 0
        self.verified_invalid_reports = 0

    def generate_request(self):
        self.most_recent_request = self.sysrand.randint(1,self.maxDomain)
        return self.most_recent_request

    def make_request(self, request=None):
        if request == None:
            request = self.generate_request()

        self.requests += 1
        return self.server.handle_request(request)

    def verify_request(self, request):
        raise NotImplementedError("Child class did not implement verify_request()")
    def __str__(self):
        raise NotImplementedError("Child class did not implement __str__()")     

    def log_not_checked(self, request):
        if request == True:
            self.unverified_valid_reports += 1
        else:
            self.unverified_invalid_reports += 1

        self._print_record(False, request)

    def log_checked(self, request):
        if request == True:
            self.verified_valid_reports += 1
        else:
            self.verified_invalid_reports += 1

        self._print_record(True, request)

    def log_state(self):
        self._print_record()

    def _print_record(self, checked=None, request=None):
        if PRINTALL == True or checked == None:
            if checked == True:
                print "Checked                - %s" % str(request)
            elif checked == False:
                print "Not Checked            - %s" % str(request)
            else:
                print "%s status:" % self.__class__.__name__

            print "    Total requests     - %d" % self.requests
            print "    Unverified valid   - %d" % self.unverified_valid_reports
            print "    Unverified invalid - %d" % self.unverified_invalid_reports
            print "    Verified valid     - %d" % self.verified_valid_reports
            print "    Verified invalid   - %d" % self.verified_invalid_reports

# This checks randomly a fixed amount of the time. That is, it will check 5% of
# the time if percentage is set to 5.
# server is the server request are being made of. 
#    Child of class Server above.
# percentage is an integer between 0 and 100.
#    0 is never checking, 100 is always checking
# maxDomain is a positive integer representing the maximum number of domains
#    defaults to 1000
class FixedCheckingClient(Client):
    def __init__(self, server, percentage, maxDomain=1000):
        super(FixedCheckingClient,self).__init__(server, maxDomain)
        self.percentage = percentage

    def __str__(self):
        return "%s - percent: %d%%" % (self.__class__.__name__ , 
                                       self.percentage)


    def verify_request(self, request):
        randNum = self.sysrand.randint(1,100)
        if randNum <= self.percentage:
            #Verify the request (which is just the value of request)
            self.log_checked(request)
            return request
        # If we're not verifying, return good status
        self.log_not_checked(request)
        return True


# This checks based on the number of good request from the server. 
# server is the server request are being made of. 
#    Child of class Server above.
# startPercentage is an integer between 0 and 100.
#    0 is never checking, 100 is always checking.
#    Starting value for self.percentage.
# floorPercentage is an integer between 0 and startPercentage.
#    The lowest value self.percentage can be.
# decrement is a small number (can be a float)
#    how much to reduce self.percentage until it reaches the floor. 
# maxDomain is a positive integer representing the maximum number of domains
#    defaults to 1000
class LinearServerBasedClient(Client):
    def __init__(self, server, startPercentage, floorPercentage, 
                 decrement, maxDomain=1000):
        super(LinearServerBasedClient,self).__init__(server, maxDomain)
        self.percentage = startPercentage
        self.ceiling = startPercentage
        self.floor = floorPercentage
        self.decrement = decrement
        self.count = 0

    def __str__(self):
        retstr  = "%s\n" % self.__class__.__name__ 
        retstr += "    percent: %d\n" % self.percentage
        retstr += "    ceiling: %d\n" % self.ceiling
        retstr += "    floor:   %d\n" % self.floor
        retstr += "    dec:     %d\n" % self.decrement
        retstr += "    count:   %d" % self.count
        return retstr


    def verify_request(self, request):
        randNum = self.sysrand.randint(1,100)
        if randNum <= self.percentage:
            #Verify the request (which is just the value of request)
            self.log_checked(request)
            if request == True:
                self.count += 1
                self.percentage -= self.decrement
                if self.percentage < self.floor:
                    self.percentage = self.floor
                return True
            #else:
            self.count = 0
            self.percentage = self.ceiling
            return False
        #Not checking, return true
        self.log_not_checked(request)
        return True


                

# This checks based on the number of good request from the server. 
# server is the server request are being made of. 
#    Child of class Server above.
# startPercentage is an integer between 0 and 100.
#    0 is never checking, 100 is always checking.
#    Starting value for self.percentage.
# floorPercentage is an integer between 0 and startPercentage.
#    The lowest value self.percentage can be.
# reduction is a number between 0 and 1, and is how much self.percentage is 
# multiplied by to reduce self.percentage for a valid response.
#    how much to reduce self.percentage until it reaches the floor. 
# maxDomain is a positive integer representing the maximum number of domains
#    defaults to 1000
class ExponentialServerBasedClient(Client):
    def __init__(self, server, startPercentage, floorPercentage, 
                 reduction, maxDomain=1000):
        super(ExponentialServerBasedClient,self).__init__(server, maxDomain)
        self.percentage = startPercentage
        self.ceiling = startPercentage
        self.floor = floorPercentage
        self.reduction = reduction
        self.count = 0

    def __str__(self):
        retstr  = "%s\n" % self.__class__.__name__ 
        retstr += "    percent: %d\n" % self.percentage
        retstr += "    ceiling: %d\n" % self.ceiling
        retstr += "    floor:   %d\n" % self.floor
        retstr += "    reduc:   %d\n" % self.reduction
        retstr += "    count:   %d" % self.count
        return retstr


    def verify_request(self, request):
        randNum = self.sysrand.randint(1,100)
        if randNum <= self.percentage:
            #Verify the request (which is just the value of request)
            self.log_checked(request)
            if request == True:
                self.count += 1
                self.percentage *= self.reduction
                if self.percentage < self.floor:
                    self.percentage = self.floor
                return True
            #else:
            self.count = 0
            self.percentage = self.ceiling
            return False
        # Not checking, return True
        self.log_not_checked(request)
        return True


# This checks based on the number of requests made per domain from the server.
# server is the cerver requests are being made of.
#    Child of class Server above.
# startPercentage is an integer between 0 and 100.
#    0 is never checking, 100 is always checking.
#    Starting value for self.percentage.
# floorPercentage is an integer between 0 and startPercentage.
#    The lowest value self.percentage can be.
# decrement is a small number (can be a float)
#    how much to reduce self.percentage until it reaches the floor. 
# multiplied by to reduce self.percentage for a valid response.
#    how much to reduce self.percentage until it reaches the floor. 
# maxDomain is a positive integer representing the maximum number of domains
#    defaults to 1000
class PerDomainLinearBasedClient(Client):
    def __init__(self, server, startPercentage, floorPercentage, 
                 decrement, maxDomain=1000):
        super(PerDomainLinearBasedClient,self).__init__(server, maxDomain)
        self.ceiling = startPercentage
        self.floor = floorPercentage
        self.decrement = decrement
        self.counts = [0] * (self.maxDomain + 1)
        self.percentages = [self.ceiling] * (self.maxDomain + 1)

    
    def verify_request(self, request):
        domain = self.most_recent_request
        randNum = self.sysrand.randint(1,100)
        if randNum <= self.percentages[domain]:
            #Verify the request (which is just the value of request)
            self.log_checked(request)
            if request == True:
                self.counts[domain] += 1
                self.percentages[domain] -= self.decrement
                if self.percentages[domain] < self.floor:
                    self.percentages[domain] = self.floor
                return True
            #else:
            self.counts[domain] = 0
            self.percentages[domain] = self.ceiling
            return False
        #Not checking, return true
        self.log_not_checked(request)
        return True

# This checks based on the number of requests made per domain from the server.
# server is the cerver requests are being made of.
#    Child of class Server above.
# startPercentage is an integer between 0 and 100.
#    0 is never checking, 100 is always checking.
#    Starting value for self.percentage.
# floorPercentage is an integer between 0 and startPercentage.
#    The lowest value self.percentage can be.
# decrement is a small number (can be a float)
#    how much to reduce self.percentage until it reaches the floor. 
# multiplied by to reduce self.percentage for a valid response.
#    how much to reduce self.percentage until it reaches the floor. 
# maxDomain is a positive integer representing the maximum number of domains
#    defaults to 1000
class PerDomainExponentialBasedClient(Client):
    def __init__(self, server, startPercentage, floorPercentage, 
                 reduction, maxDomain=1000):
        super(PerDomainExponentialBasedClient,self).__init__(server, maxDomain)
        self.ceiling = startPercentage
        self.floor = floorPercentage
        self.reduction = reduction
        self.counts = [0] * (self.maxDomain + 1)
        self.percentages = [self.ceiling] * (self.maxDomain + 1)

    
    def verify_request(self, request):
        domain = self.most_recent_request
        randNum = self.sysrand.randint(1,100)
        if randNum <= self.percentages[domain]:
            #Verify the request (which is just the value of request)
            self.log_checked(request)
            if request == True:
                self.counts[domain] += 1
                self.percentages[domain] *= self.reduction
                if self.percentages[domain] < self.floor:
                    self.percentages[domain] = self.floor
                return True
            #else:
            self.counts[domain] = 0
            self.percentages[domain] = self.ceiling
            return False
        #Not checking, return true
        self.log_not_checked(request)
        return True


def run_sim(client, times):
    for i in range(times):
        client.verify_request(fcl.make_request())

    print str(client)
    client.log_state()
    print "\n\n"

from simulate import *
rs = RandomServer(10)
fcl = FixedCheckingClient(rs, 10, 10)
fcl = PerDomainLinearBasedClient(rs, 100, 10, 1)

def run_fcl_sim(times):
   for i in range(times):
       if fcl.verify_request(fcl.make_request()) == False:
            print "ERROR"
