import urllib.request
import urllib.error
import json
import time

BASE_URL = "http://localhost:8080"

def test_n8n_endpoint():
    print("Testing n8n integration endpoint...")
    
    url = f"{BASE_URL}/api/reports/from-n8n"
    
    payload = {
        "driver": "Verification Bot",
        "date": "2025-11-18",
        "venue": "Virtual Circuit",
        "event": "Integration Test",
        "accident_damage": "Automated test of n8n integration endpoint.",
        "parts": [
            {
                "part_number": "TEST-VERIFY-001",
                "part": "Verification Module",
                "likelihood": "Highly Likely",
                "price": 123.45,
                "qty": 1
            }
        ]
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            response_body = response.read().decode('utf-8')
            data = json.loads(response_body)
            
            if status_code == 201:
                if data.get("success") and data.get("status") == "pending":
                    print("✅ SUCCESS: Report created successfully via n8n endpoint.")
                    print(f"   Report ID: {data['report']['id']}")
                    print(f"   Status: {data['report']['status']}")
                    return data['report']['id']
                else:
                    print(f"❌ FAILED: Unexpected response content: {data}")
            else:
                print(f"❌ FAILED: Status code {status_code}")
                print(f"   Response: {response_body}")
            
    except urllib.error.HTTPError as e:
        print(f"❌ FAILED: HTTP Error {e.code}")
        print(f"   Response: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        
    return None

def verify_pending_report(report_id):
    if not report_id:
        return
        
    print(f"\nVerifying report {report_id} is in pending list...")
    
    url = f"{BASE_URL}/api/reports/pending"
    
    try:
        with urllib.request.urlopen(url) as response:
            status_code = response.getcode()
            response_body = response.read().decode('utf-8')
            reports = json.loads(response_body)
            
            if status_code == 200:
                found = False
                for report in reports:
                    if report['id'] == report_id:
                        found = True
                        print("✅ SUCCESS: Report found in pending list.")
                        break
                
                if not found:
                    print(f"❌ FAILED: Report {report_id} not found in pending list.")
            else:
                print(f"❌ FAILED: Status code {status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    report_id = test_n8n_endpoint()
    verify_pending_report(report_id)
