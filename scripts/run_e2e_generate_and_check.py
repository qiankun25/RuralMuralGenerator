"""
端到端本地验证脚本

用法（PowerShell）:
    .\maral-generator-env\Scripts\Activate.ps1
    python .\scripts\run_e2e_generate_and_check.py

脚本行为：
- POST /api/generate-image 创建任务（在缺少 API key 的情况下后端会使用 mock 图像并把它复制到 image_output_dir）
- 轮询 /api/task/{task_id} 直到状态为 completed 或 failed
- 当完成时，下载 result.images[0].url 到本地文件并报告结果
"""

import os
import time
import requests
from datetime import datetime

API_BASE = os.getenv('API_BASE_URL', 'http://localhost:8000')

def create_task():
    url = f"{API_BASE.rstrip('/')}/api/generate-image"
    payload = {
        "design_option": "Test mock design prompt for e2e check",
        "style_preference": "traditional"
    }
    print(f"POST {url} -> payload={payload}")
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    task_id = data.get('task_id')
    print(f"Created task_id: {task_id}")
    return task_id


def poll_task(task_id, timeout_seconds=120):
    url = f"{API_BASE.rstrip('/')}/api/task/{task_id}"
    start = time.time()
    while True:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                print(f"GET {url} returned {r.status_code}")
                time.sleep(2)
                continue
            data = r.json()
            status = data.get('status')
            progress = data.get('progress')
            print(f"status={status}, progress={progress}")

            if status == 'completed':
                return data
            if status == 'failed':
                raise RuntimeError(f"Task failed: {data.get('error')}")
        except Exception as e:
            print(f"Polling error: {e}")
        if time.time() - start > timeout_seconds:
            raise TimeoutError("Polling timed out")
        time.sleep(2)


def download_image(img_info, dest_dir='./tmp_e2e'):
    os.makedirs(dest_dir, exist_ok=True)
    url = img_info.get('url')
    local_path = img_info.get('local_path')

    if url:
        print(f"Downloading from URL: {url}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        filename = os.path.basename(url)
        if not filename:
            filename = f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        dest = os.path.join(dest_dir, filename)
        with open(dest, 'wb') as f:
            f.write(r.content)
        print(f"Downloaded to: {dest}")
        return dest
    elif local_path and os.path.exists(local_path):
        print(f"Local path exists on this machine: {local_path}")
        return local_path
    else:
        raise FileNotFoundError('No accessible URL or local_path for image')


def main():
    try:
        task_id = create_task()
        result = poll_task(task_id, timeout_seconds=180)
        print('Task result:', result.get('result'))
        images = (result.get('result') or {}).get('images')
        if not images:
            print('No images returned')
            return
        img_info = images[0]
        downloaded = download_image(img_info)
        print('E2E check succeeded, downloaded image at:', downloaded)
    except Exception as e:
        print('E2E check failed:', e)

if __name__ == '__main__':
    main()
