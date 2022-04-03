#allow easy sharing of a flag between classes to set/clear
class MockFlag:
    def __init__(self, initial_value = True):
        self.value = initial_value