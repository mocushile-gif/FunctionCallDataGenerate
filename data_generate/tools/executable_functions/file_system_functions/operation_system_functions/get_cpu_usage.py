import psutil
import time
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

def get_cpu_usage(duration=1, interval=0.1):
    """
    Get detailed CPU usage over time, including timestamped sampling.

    Parameters:
    - duration (int): Total monitoring time in seconds.
    - interval (float): Sampling interval in seconds.

    Returns:
    - (bool, dict or str): On success, returns a dictionary with timestamped samples and average. On failure, returns error message.
    """
    try:
        usage_samples = []
        start_time = time.time()

        while time.time() - start_time < duration:
            usage = psutil.cpu_percent(interval=interval)
            timestamp = datetime.now().isoformat(timespec='seconds')
            usage_samples.append({
                "timestamp": timestamp,
                "usage": round(usage, 2)
            })

        average_usage = round(sum([s["usage"] for s in usage_samples]) / len(usage_samples), 2)

        result = {
            "interval": interval,
            "duration": duration,
            "average_usage": average_usage,
            "unit": "%",
            "samples": usage_samples
        }

        return True, result
    except Exception as e:
        return False, str(e)


if __name__ == '__main__':
    success, output = get_cpu_usage(duration=2, interval=0.5)
    print(output)
