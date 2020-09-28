import psutil
import pandas as pd
import time

def running_aps(interval = 20):

    df = pd.DataFrame(columns=['pid', 'name', 'username', 'status', 'cpu_percent'])
    for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent']):
        pass

    for i in range(interval):
        print("#" * (interval-i))
        time.sleep(1)
    
    for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent']):
        df = df.append(proc.info, ignore_index=True)

    df = df.sort_values(['cpu_percent'], ascending=False)
    return df

if __name__ == "__main__":
    df = running_aps()
    print(df)