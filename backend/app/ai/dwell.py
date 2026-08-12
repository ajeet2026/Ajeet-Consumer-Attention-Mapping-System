class DwellCalculator:
    @staticmethod
    def calculate_duration(start_time, end_time):
        """
        Calculates the duration between two datetime objects in seconds.
        """
        if not start_time or not end_time:
            return 0.0
        return float((end_time - start_time).total_seconds())
