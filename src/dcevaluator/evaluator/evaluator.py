from loguru import logger
import time
from threading import Thread

class Evaluator:
    def __init__(self, event_handler, 
                       controller, 
                       nbr_turns_limit = 10,
                       max_time_to_wait = 10 * 60,
                       delay_between_check_interval = 1/60,
                       delay_before_launch_car = 5
                       ):
        self.event_handler = event_handler
        self.controller = controller
        self.nbr_turns_limit = nbr_turns_limit
        self.max_time_to_wait = max_time_to_wait
        self.delay_between_check_interval = delay_between_check_interval
        self.delay_before_launch_car = delay_before_launch_car

        self.event_handler.on_car_loaded = self.wait_car_controller

        self.time_start_waiting = time.time()

    def wait_car_controller(self, *args, **kwargs):
        def wait_car_controller_thread_func():
            self.time_start_waiting = time.time()
            while not self.event_handler.car_controller_is_ready:
                time.sleep(self.delay_between_check_interval)
                if time.time() - self.time_start_waiting > self.max_time_to_wait:
                    logger.critical("Timeout : No car controller ready to drive !")
                    raise RuntimeError("Timeout : No car controller ready to drive !")
            self.run()
        
        self.run_thread = Thread(target=wait_car_controller_thread_func)
        self.run_thread.start()
    
    def run(self):
        logger.success("[Evaluation Begin]")
        self.event_handler.car_is_driving = True
        