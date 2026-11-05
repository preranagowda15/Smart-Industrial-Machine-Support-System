"""
scripts/capture_browser_demo.py - Playwright automated UI verification & screenshot capture.
Exercises all UI interactions:
1. Login page & demo account pills
2. Operator upload & normal plate inspection
3. Operator upload & defective plate inspection
4. Validation rejection (corrupt_image.png)
5. Inspection detail & Supervisor review form submission
6. Evaluation page with 2x2 confusion matrix & recall KPI
7. Admin dashboard with user list & SHA256 integrity verification
"""

import os
import time
from playwright.sync_api import sync_playwright

os.makedirs('media/screenshots', exist_ok=True)
chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=chrome_path, headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 850})

        # 1. Login Page
        page.goto('http://127.0.0.1:8000/login/')
        page.wait_for_selector('#login-form')
        page.screenshot(path='media/screenshots/screenshot_1_login.png')
        print('1. Captured login screenshot.')

        # Login as Operator
        page.fill('#username', 'operator1')
        page.fill('#password', 'Operator123!')
        page.click('#login-submit-btn')
        page.wait_for_url('http://127.0.0.1:8000/upload/')
        page.wait_for_selector('#dropzone')

        # 2. Upload Normal Plate (inspection_001.png)
        page.set_input_files('#file-input', 'Samples/images/inspection_001.png')
        page.click('#inspect-btn')
        page.wait_for_selector('#result-card:not(.d-none)', timeout=10000)
        time.sleep(1)
        page.screenshot(path='media/screenshots/screenshot_2_upload_normal.png')
        print('2. Captured upload normal screenshot.')

        # 3. Upload Defective Plate (inspection_035.png)
        page.click('button:has-text("New Inspection")')
        page.set_input_files('#file-input', 'Samples/images/inspection_035.png')
        page.click('#inspect-btn')
        page.wait_for_selector('#result-card:not(.d-none)', timeout=10000)
        time.sleep(1)
        page.screenshot(path='media/screenshots/screenshot_3_upload_defective.png')
        print('3. Captured upload defective screenshot.')

        # 4. Upload Validation Rejection (corrupt_image.png)
        page.click('button:has-text("New Inspection")')
        page.set_input_files('#file-input', 'Validation/corrupt_image.png')
        page.click('#inspect-btn')
        page.wait_for_selector('#upload-alert:not(.d-none)', timeout=10000)
        time.sleep(1)
        page.screenshot(path='media/screenshots/screenshot_4_validation_rejection.png')
        print('4. Captured validation rejection screenshot.')

        # 5. Inspection Detail with Supervisor Review
        # Logout
        page.click('#logout-btn')
        page.wait_for_url('http://127.0.0.1:8000/login/')

        # Login as Supervisor
        page.fill('#username', 'supervisor1')
        page.fill('#password', 'Supervisor123!')
        page.click('#login-submit-btn')
        page.wait_for_url('http://127.0.0.1:8000/upload/')

        # Navigate to history and click view on the defective inspection
        page.goto('http://127.0.0.1:8000/history/')
        page.wait_for_selector('#history-table-body a', timeout=10000)
        page.click('#history-table-body a')
        page.wait_for_selector('#supervisor-review-form-container:not(.d-none)', timeout=10000)

        # Submit Supervisor Review
        page.select_option('#review-decision', 'CONFIRMED')
        page.fill('#review-comment', 'Defect verified: crack and surface pit confirmed by supervisor.')
        page.click('#submit-review-btn')
        time.sleep(1.5)
        page.screenshot(path='media/screenshots/screenshot_5_inspection_detail_review.png')
        print('5. Captured inspection detail & review screenshot.')

        # 6. Evaluation Dashboard
        page.goto('http://127.0.0.1:8000/evaluation/')
        page.wait_for_selector('#kpi-recall', timeout=10000)
        time.sleep(2)
        page.screenshot(path='media/screenshots/screenshot_6_evaluation_dashboard.png')
        print('6. Captured evaluation dashboard screenshot.')

        # 7. Admin Dashboard & Integrity Check
        page.click('#logout-btn')
        page.wait_for_url('http://127.0.0.1:8000/login/')

        # Login as Admin
        page.fill('#username', 'admin1')
        page.fill('#password', 'Admin123!')
        page.click('#login-submit-btn')
        page.wait_for_url('http://127.0.0.1:8000/upload/')

        page.goto('http://127.0.0.1:8000/admin-dashboard/')
        page.wait_for_selector('#integrity-table-body tr', timeout=10000)
        time.sleep(2)
        page.screenshot(path='media/screenshots/screenshot_7_admin_integrity.png')
        print('7. Captured admin integrity dashboard screenshot.')

        browser.close()
        print('ALL 7 SCREENSHOTS CAPTURED SUCCESSFULLY!')


if __name__ == '__main__':
    run()

