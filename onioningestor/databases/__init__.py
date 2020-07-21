import sys
import time
import schedule
import threading

class StorageScheduler():
    def __init__(self, storage, **kwargs):
        self.storage = storage
        self.name = self.storage.name

    def save_pastie(self, pastie, timeout):
        raise NotImplementedError


class StorageSync(StorageScheduler):
    ### synchronously save onions ###
    def save_pastie(self, pastie, timeout):
        self.storage.save_pastie(pastie)


# LATER: implement an async class
class StorageThread(threading.Thread, StorageScheduler):
    def __init__(self, logger, storage, **kwargs):
        threading.Thread.__init__(self)
        StorageScheduler.__init__(self, storage, **kwargs)
        self.logger = logger
        try:
            size = int(kwargs['queue_size'])
        except Exception:
            size = 0
        self.queue = Queue(size)
        self.kill_received = False

    def run(self):
        self.logger.info('{0}: Thread for saving pasties started'.format(self.name))
        # loop over the queue
        while not self.kill_received:
            # pastie = None
            try:
                # grabs pastie from queue
                pastie = self.queue.get(True, 5)
                # save the pasties in each storage
                self.storage.save_pastie(pastie)
            except Empty:
                pass
            # catch unknown errors
            except Exception as e:
                self.logger.error("{0}: Thread for saving pasties crashed unexpectectly, recovering...: {1}".format(self.name, e))
                self.logger.debug(traceback.format_exc())
            finally:
                # to be on the safe side of gf
                del(pastie)
                # signals to queue job is done
                self.queue.task_done()
        self.logger.info('{0}: Thread for saving pasties terminated'.format(self.name))

    def save_pastie(self, pastie, timeout):
        try:
            self.logger.debug('{0}: queueing pastie {1} for saving'.format(self.name, pastie.url))
            self.queue.put(pastie, True, timeout)
        except Full:
            self.logger.error('{0}: unable to save pastie[{1}]: queue is full'.format(self.name, pastie.url))


class StorageDispatcher():
    """Dispatcher will then take care of dispatching onions to the right databases. 
    Each database thread will read in the task and will handle it."""
    def __init__(self, logger):
        self.logger = logger
        self.__storage = []
        self.lock = threading.Lock()

    def add_storage(self, thread_storage):
        self.__storage.append(thread_storage)

    def save_pastie(self, pastie, timeout=5):
        self.logger.debug('Saving to database')
        for t in self.__storage:
            t.save_pastie(pastie, timeout)

class PastieStorage():
    def __init__(self, **kwargs):
        self.lookup = kwargs.get('lookup', False)
        self.name = kwargs.get('name', self.__class__.__name__)
        try:
            self.logger.debug('{0}: initializing storage backend'.format(self.name))
            self.__init_storage__(**kwargs)
        except Exception as e:
            self.logger.error('{0}: unable to initialize storage backend: {1}'.format(self.name, e))
            raise

    def format_directory(self, directory):
        d = datetime.now()
        year = str(d.year)
        month = str(d.month)
        # prefix month and day with "0" if it is only one digit
        if len(month) < 2:
            month = "0" + month
        day = str(d.day)
        if len(day) < 2:
            day = "0" + day
        return directory + os.sep + year + os.sep + month + os.sep + day

    def __init_storage__(self, **kwargs):
        raise NotImplementedError

    def __save_pastie__(self, pastie):
        raise NotImplementedError

    def save_pastie(self, pastie):
        try:
            start = time.time()
            self.logger.debug('{0}: saving pastie[{1}]'.format(self.name, pastie.url))
            self.__save_pastie__(pastie)
            delta = time.time() - start
            self.logger.debug('{0}: pastie[{1}] saved in {2}s'.format(self.name, pastie.url, delta))
        except Exception as e:
            self.logger.error('{0}: unable to save pastie[{1}]: {2}'.format(self.name, pastie.url, e))
            pass
            #raise

class Notifier(object):
    def __init__(self, logger, **kwargs):
        self.logger = logger
    
    def send(self):
        raise NotImplementedError()

    def scheduledEvery(self, time="10:30"):
        self.logger.info(f'Scheduled task everyday as {time}')
        schedule.every().day.at(time).do(self.send)
        schedule.run_pending()

