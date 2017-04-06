from pylab import *


class Environment:
    def __init__(self, eyetracker_accuracy, eyetracker_distance, screen_res_x, screen_res_y, screen_size_diagonal):
        # Provide the degree of accuracy of an eye tracker, such as 0.5
        self.eyetracker_accuracy = eyetracker_accuracy
        # Provide the distance between the eye tracker and the participants in centimeters, such as 60
        self.eyetracker_distance = eyetracker_distance
        # Provide the X resolution of the screen, such as 1280
        self.screen_res_x = screen_res_x
        # Provide the Y resolution of the screen, such as 1024
        self.screen_res_y = screen_res_y
        # Provide the size of the screen in inches, such as 17.
        self.screen_size_diagonal = screen_size_diagonal

    def get_ppi(self):
        diagonal_res = sqrt(pow(self.screen_res_x, 2) + pow(self.screen_res_y, 2))
        ppi = diagonal_res / self.screen_size_diagonal

        return ppi

    def get_error_rate_area(self):
        # Calculate error rate area (in cm by default)
        error_rate_area_cm = tan(radians(self.eyetracker_accuracy)) * self.eyetracker_distance
        error_rate_area_pixels = (error_rate_area_cm * self.get_ppi()) / 2.54

        return round(error_rate_area_pixels, 2)



